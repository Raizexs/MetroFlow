import { useMemo, useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { useAnimatedValue } from "../hooks/useAnimatedValue";
import { LIVE_STATUS_LABEL, TRAIN_DEPARTED_LABEL } from "../config/polling";
import { formatVagonLabel } from "../lib/formatVagon";
import {
  efeDensityLabel,
  efeDensityPercent,
  getEfeServiceContext,
} from "../lib/efeSchedule";
import { prefersReducedMotion } from "../lib/motion";
import type { OccupationResponse } from "../types/occupation";

const STATUS_STYLES = {
  normal: {
    badge: "bg-emerald-500/20 text-emerald-300 ring-emerald-500/40",
    bar: "bg-emerald-500",
    glow: "",
    label: "Normal",
  },
  warning: {
    badge: "bg-amber-500/20 text-amber-300 ring-amber-500/40",
    bar: "bg-amber-500",
    glow: "shadow-amber-500/10",
    label: "Advertencia",
  },
  critical: {
    badge: "bg-red-500/20 text-red-300 ring-red-500/40",
    bar: "bg-red-500",
    glow: "shadow-red-500/30 ring-2 ring-red-500/50 animate-pulse-slow",
    label: "Crítico",
  },
} as const;

interface VagonCardProps {
  data: OccupationResponse;
  refreshing?: boolean;
  lastUpdated: Date | null;
  lastTelemetryAt: Date | null;
  telemetryActive: boolean;
  delta?: number;
}

export function VagonCard({
  data,
  refreshing,
  lastUpdated,
  lastTelemetryAt,
  telemetryActive,
  delta = 0,
}: VagonCardProps) {
  const efe = useMemo(() => getEfeServiceContext(), []);
  const densityPct = useMemo(
    () => efeDensityPercent(data.headcount, efe.intervalMinutes),
    [data.headcount, efe.intervalMinutes],
  );
  const densityHint = useMemo(() => efeDensityLabel(densityPct), [densityPct]);

  const styles = STATUS_STYLES[data.status];
  const animatedCount = useAnimatedValue(data.headcount);
  const countRef = useRef<HTMLParagraphElement>(null);

  useGSAP(
    () => {
      if (prefersReducedMotion() || delta === 0 || !countRef.current) return;
      gsap.fromTo(
        countRef.current,
        { scale: 1 },
        { scale: 1.06, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out" },
      );
    },
    { dependencies: [delta], scope: countRef },
  );

  return (
    <article
      className={`relative overflow-hidden rounded-2xl border border-metro-border/80 bg-gradient-to-br from-metro-panel via-metro-panel/60 to-slate-900/40 p-8 shadow-2xl backdrop-blur-md ${styles.glow}`}
    >
      <div className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-sky-500/10 blur-3xl" />

      <header className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Densidad en andén · {formatVagonLabel(data.vagon_id)}
          </p>
          <p className="mt-1 text-sm text-slate-400">
            Telemetría en zona · tren cada ~{efe.intervalMinutes} min
          </p>
        </div>
        <span
          className={`inline-flex shrink-0 items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${styles.badge}`}
        >
          {styles.label}
        </span>
      </header>

      <p
        ref={countRef}
        className="font-display text-6xl font-bold tabular-nums tracking-tight text-white"
      >
        {animatedCount}
        <span className="ml-2 text-xl font-medium text-slate-400">en zona</span>
      </p>

      {delta !== 0 && (
        <p
          className={`mt-2 text-sm font-medium ${
            delta > 0 ? "text-emerald-400" : "text-amber-300"
          }`}
        >
          {delta > 0 ? "↑" : "↓"} {Math.abs(delta)} respecto a la lectura anterior
          {delta > 0 && efe.isPeakWeekday && " · subida típica antes del tren"}
        </p>
      )}

      <div className="mt-6">
        <div className="mb-2 flex justify-between text-xs text-slate-400">
          <span>Densidad calibrada EFE</span>
          <span>{densityPct}%</span>
        </div>
        <div className="h-2.5 overflow-hidden rounded-full bg-slate-800/90">
          <div
            className={`h-full rounded-full transition-[width] duration-700 ease-out ${styles.bar}`}
            style={{ width: `${densityPct}%` }}
          />
        </div>
        <p className="mt-2 text-xs text-slate-500">{densityHint}</p>
        <p className="mt-1 text-[10px] text-slate-600">
          Tren cada ~{efe.intervalMinutes} min · detención {efe.dwellLabel}
        </p>
      </div>

      <footer className="mt-6 flex items-center justify-between border-t border-metro-border/60 pt-4 text-xs text-slate-500">
        <span>
          {lastUpdated
            ? `Actualizado ${lastUpdated.toLocaleTimeString("es-CL")}`
            : "—"}
        </span>
        <span className="flex items-center gap-2">
          {telemetryActive ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-40" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-sky-400" />
              </span>
              {refreshing ? "Sincronizando…" : LIVE_STATUS_LABEL}
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-slate-500" />
              {TRAIN_DEPARTED_LABEL}
              {lastTelemetryAt && (
                <span className="text-slate-600">
                  · última detención {lastTelemetryAt.toLocaleTimeString("es-CL")}
                </span>
              )}
            </>
          )}
        </span>
      </footer>
    </article>
  );
}
