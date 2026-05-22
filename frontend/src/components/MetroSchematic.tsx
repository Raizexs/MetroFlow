import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { formatVagonLabel } from "../lib/formatVagon";
import { efeDensityPercent, getEfeServiceContext } from "../lib/efeSchedule";
import { prefersReducedMotion } from "../lib/motion";
import type { OccupationStatus } from "../types/occupation";

const ZONE_COLORS: Record<OccupationStatus, string> = {
  normal: "#10b981",
  warning: "#f59e0b",
  critical: "#ef4444",
};

interface MetroSchematicProps {
  status: OccupationStatus;
  headcount: number;
  vagonId: string;
  delta?: number;
}

export function MetroSchematic({
  status,
  headcount,
  vagonId,
  delta = 0,
}: MetroSchematicProps) {
  const fill = ZONE_COLORS[status];
  const efe = getEfeServiceContext();
  const densityPct = efeDensityPercent(headcount, efe.intervalMinutes);
  const intensity = Math.min(1, densityPct / 100);
  const svgRef = useRef<SVGSVGElement>(null);

  useGSAP(
    () => {
      if (prefersReducedMotion() || !svgRef.current) return;
      gsap.fromTo(
        ".zone-block",
        { opacity: 0.15 },
        {
          opacity: 0.2 + intensity * 0.65,
          duration: 0.6,
          stagger: 0.05,
          ease: "power2.out",
        },
      );
    },
    { dependencies: [headcount, status], scope: svgRef },
  );

  useGSAP(
    () => {
      if (prefersReducedMotion() || delta === 0 || !svgRef.current) return;
      gsap.fromTo(
        svgRef.current,
        { filter: "drop-shadow(0 0 0 transparent)" },
        {
          filter: "drop-shadow(0 0 12px rgba(56,189,248,0.5))",
          duration: 0.3,
          yoyo: true,
          repeat: 1,
        },
      );
    },
    { dependencies: [delta], scope: svgRef },
  );

  return (
    <div className="rounded-2xl border border-metro-border/80 bg-metro-panel/50 p-6 shadow-lg backdrop-blur-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Plano del vagón · densidad estimada
        </h3>
        <span className="font-display rounded-lg border border-metro-border bg-metro-bg/60 px-3 py-1 text-sm font-semibold text-sky-200">
          {formatVagonLabel(vagonId)}
        </span>
      </div>

      <svg
        ref={svgRef}
        viewBox="0 0 520 140"
        className="w-full"
        role="img"
        aria-label={`Esquema ${formatVagonLabel(vagonId)} con estado ${status}`}
      >
        <defs>
          <linearGradient id="heatGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={fill} stopOpacity={0.15 + intensity * 0.2} />
            <stop offset="50%" stopColor={fill} stopOpacity={0.35 + intensity * 0.35} />
            <stop offset="100%" stopColor={fill} stopOpacity={0.15 + intensity * 0.2} />
          </linearGradient>
        </defs>

        <rect
          x="10"
          y="50"
          width="500"
          height="50"
          rx="8"
          fill="#1e293b"
          stroke="#334155"
          strokeWidth="2"
        />
        <rect x="10" y="50" width="500" height="50" rx="8" fill="url(#heatGrad)" />

        {[0, 1, 2, 3, 4].map((i) => (
          <rect
            key={i}
            className="zone-block"
            x={30 + i * 95}
            y="58"
            width="75"
            height="34"
            rx="4"
            fill={fill}
            opacity={0.2 + intensity * 0.5}
            stroke={fill}
            strokeWidth="1"
            strokeOpacity="0.5"
          />
        ))}

        <circle cx="30" cy="75" r="14" fill="#0f172a" stroke="#64748b" strokeWidth="2" />
        <circle cx="490" cy="75" r="14" fill="#0f172a" stroke="#64748b" strokeWidth="2" />
        <text
          x="260"
          y="35"
          textAnchor="middle"
          fill="#94a3b8"
          fontSize="11"
          fontFamily="system-ui"
        >
          FRENTE
        </text>
        <text
          x="260"
          y="125"
          textAnchor="middle"
          fill="#64748b"
          fontSize="10"
          fontFamily="system-ui"
        >
          {headcount} en zona · densidad EFE {densityPct}% · tren ~{efe.intervalMinutes} min
        </text>
      </svg>

      <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-500" /> Normal
        </span>
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-amber-500" /> Advertencia
        </span>
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-red-500" /> Crítico
        </span>
      </div>
    </div>
  );
}
