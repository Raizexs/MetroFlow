import { useMemo, useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { API_URL } from "../api/client";
import { TRAIN_DEPARTED_LABEL } from "../config/polling";
import { prefersReducedMotion } from "../lib/motion";
import type { HistoryPoint } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";

interface SystemPipelineProps {
  apiOnline: boolean | null;
  lastSync: Date | null;
  headcount: number | null;
  historyPoints: HistoryPoint[];
  delta?: number;
  telemetryActive?: boolean;
}

const LAYERS = [
  {
    id: "edge",
    tag: "Edge · IA",
    title: "YOLO + línea virtual",
    detail: "Inferencia local, sin video al cloud",
    color: "from-violet-500/20 to-violet-600/5",
    ring: "ring-violet-500/30",
    dot: "#a78bfa",
  },
  {
    id: "paas",
    tag: "PaaS · API",
    title: "FastAPI + PostgreSQL",
    detail: "Telemetría anonimizada (Render)",
    color: "from-sky-500/20 to-cyan-600/5",
    ring: "ring-sky-500/30",
    dot: "#38bdf8",
  },
  {
    id: "saas",
    tag: "SaaS · Panel",
    title: "Dashboard operador",
    detail: "Visualización en tiempo real (Vercel)",
    color: "from-emerald-500/20 to-teal-600/5",
    ring: "ring-emerald-500/30",
    dot: "#34d399",
  },
] as const;

const W = 720;
const H = 88;
const PAD = { t: 10, r: 20, b: 18, l: 20 };
const CHART_W = W - PAD.l - PAD.r;
const CHART_H = H - PAD.t - PAD.b;

/** Centros bajo cada card (3 columnas). */
const ANCHOR_X = [
  PAD.l + CHART_W / 6,
  PAD.l + CHART_W / 2,
  PAD.l + CHART_W * (5 / 6),
] as const;

function yForHeadcount(h: number, max = VAGON_CAPACITY): number {
  const clamped = Math.max(0, Math.min(h, max));
  return PAD.t + CHART_H * (1 - clamped / max);
}

function buildSparkPath(values: number[]): string {
  if (values.length === 0) return "";
  if (values.length === 1) {
    const y = yForHeadcount(values[0]);
    return `M ${PAD.l} ${y} L ${PAD.l + CHART_W} ${y}`;
  }
  const step = CHART_W / (values.length - 1);
  return values
    .map((v, i) => {
      const x = PAD.l + i * step;
      const y = yForHeadcount(v);
      return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
}

function buildAreaPath(values: number[]): string {
  const line = buildSparkPath(values);
  if (!line) return "";
  const baseY = PAD.t + CHART_H;
  const lastX = PAD.l + CHART_W;
  return `${line} L ${lastX} ${baseY} L ${PAD.l} ${baseY} Z`;
}

function buildConnectorPath(nodes: [number, number, number]): string {
  return nodes
    .map((h, i) => {
      const x = ANCHOR_X[i];
      const y = yForHeadcount(h);
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
}

function resolveSeries(
  history: HistoryPoint[],
  headcount: number | null,
): { spark: number[]; nodes: [number, number, number] } {
  const spark = history.map((p) => p.headcount);
  const current = headcount ?? spark[spark.length - 1] ?? 0;

  if (spark.length === 0) {
    return { spark: [current], nodes: [current, current, current] };
  }
  if (spark.length === 1) {
    return { spark: [spark[0], current], nodes: [spark[0], spark[0], current] };
  }

  const last3 = spark.slice(-3);
  while (last3.length < 3) {
    last3.unshift(last3[0] ?? current);
  }
  const nodes: [number, number, number] = [last3[0], last3[1], last3[2]];

  return { spark, nodes };
}

export function SystemPipeline({
  apiOnline,
  lastSync,
  headcount,
  historyPoints,
  delta = 0,
  telemetryActive = false,
}: SystemPipelineProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const lineRef = useRef<SVGPathElement>(null);
  const connectorRef = useRef<SVGPathElement>(null);

  const { spark, nodes } = useMemo(
    () => resolveSeries(historyPoints, headcount),
    [historyPoints, headcount],
  );

  const sparkPath = useMemo(() => buildSparkPath(spark), [spark]);
  const areaPath = useMemo(() => buildAreaPath(spark), [spark]);
  const connectorPath = useMemo(() => buildConnectorPath(nodes), [nodes]);

  useGSAP(
    () => {
      if (prefersReducedMotion()) return;
      const targets = [lineRef.current, connectorRef.current].filter(Boolean);
      if (targets.length === 0) return;
      gsap.fromTo(
        targets,
        { opacity: 0.5 },
        { opacity: 1, duration: 0.35, ease: "power2.out" },
      );
      if (delta !== 0 && connectorRef.current && telemetryActive) {
        gsap.fromTo(
          connectorRef.current,
          { strokeWidth: 2.5 },
          { strokeWidth: 3.5, duration: 0.2, yoyo: true, repeat: 1 },
        );
      }
    },
    { dependencies: [sparkPath, connectorPath, delta], scope: rootRef },
  );

  return (
    <section
      ref={rootRef}
      className="overflow-hidden rounded-2xl border border-metro-border/80 bg-gradient-to-br from-metro-panel/90 via-metro-panel/50 to-metro-bg/80 p-6 shadow-xl backdrop-blur-md"
      aria-label="Arquitectura MetroFlow conectada"
    >
      <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400/90">
            Flujo en producción
          </p>
          <h2 className="font-display mt-1 text-xl font-semibold text-white">
            Edge IA → API → Dashboard
          </h2>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-metro-border bg-metro-bg/60 px-3 py-1.5 text-xs text-slate-400">
          <span
            className={`h-2 w-2 rounded-full ${
              apiOnline ? "bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]" : "bg-slate-500"
            }`}
          />
          {apiOnline
            ? telemetryActive
              ? "Detención en andén · telemetría activa"
              : TRAIN_DEPARTED_LABEL
            : "Sin enlace API"}
          {headcount !== null && telemetryActive && (
            <span className="ml-2 border-l border-metro-border pl-2 font-mono text-sky-300">
              {headcount} en zona
            </span>
          )}
        </div>
      </div>

      <div className="grid gap-0 md:grid-cols-3">
        {LAYERS.map((layer, i) => (
          <div key={layer.id} className="px-1 pb-0">
            <div
              className={`pipeline-card rounded-xl border border-metro-border/60 bg-gradient-to-br ${layer.color} p-4 ring-1 ring-inset ${layer.ring}`}
            >
              <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                {layer.tag}
              </p>
              <p className="mt-2 font-display text-sm font-semibold text-white">{layer.title}</p>
              <p className="mt-1 text-xs leading-relaxed text-slate-400">{layer.detail}</p>
            </div>
            <p className="mt-2 text-center font-mono text-[10px] text-slate-500">
              {nodes[i]} pax
            </p>
          </div>
        ))}
      </div>

      <div className="relative -mt-1 px-1">
        <svg
          viewBox={`0 0 ${W} ${H}`}
          className="w-full"
          role="img"
          aria-label={`Telemetría: ${headcount ?? 0} pasajeros, gráfico bajo las tres capas`}
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="pipelineArea" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="pipelineStroke" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#a78bfa" />
              <stop offset="50%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#34d399" />
            </linearGradient>
          </defs>

          {/* Línea de fondo: historial completo */}
          {areaPath && (
            <path d={areaPath} fill="url(#pipelineArea)" stroke="none" opacity={0.6} />
          )}
          {sparkPath && (
            <path
              ref={lineRef}
              d={sparkPath}
              fill="none"
              stroke="#334155"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />
          )}

          {/* Conexión en 3 puntos bajo las cards */}
          {connectorPath && (
            <path
              ref={connectorRef}
              d={connectorPath}
              fill="none"
              stroke="url(#pipelineStroke)"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />
          )}

          {/* Nodos bajo cada columna */}
          {nodes.map((h, i) => (
            <g key={LAYERS[i].id}>
              <line
                x1={ANCHOR_X[i]}
                y1={yForHeadcount(h)}
                x2={ANCHOR_X[i]}
                y2={PAD.t + CHART_H}
                stroke={LAYERS[i].dot}
                strokeOpacity={0.25}
                strokeWidth="1"
                strokeDasharray="3 3"
              />
              <circle
                cx={ANCHOR_X[i]}
                cy={yForHeadcount(h)}
                r="5"
                fill={LAYERS[i].dot}
                stroke="#0f172a"
                strokeWidth="2"
              />
            </g>
          ))}
        </svg>
      </div>

      <p className="mt-2 truncate font-mono text-[10px] text-slate-600">
        API: {API_URL}
        {lastSync ? ` · última lectura ${lastSync.toLocaleTimeString("es-CL")}` : ""}
        {spark.length > 1 ? ` · ${spark.length} muestras en el trazado` : ""}
      </p>
    </section>
  );
}
