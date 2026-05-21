import type { OccupationResponse } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";

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
}

function formatVagonLabel(vagonId: string): string {
  const match = vagonId.match(/vagon_(\d+)/i);
  if (match) return `Vagón ${match[1]}`;
  return vagonId.replace(/_/g, " ");
}

export function VagonCard({ data, refreshing, lastUpdated }: VagonCardProps) {
  const styles = STATUS_STYLES[data.status];
  const occupancyPct = Math.min(100, Math.round((data.headcount / VAGON_CAPACITY) * 100));

  return (
    <article
      className={`relative overflow-hidden rounded-2xl border border-metro-border/80 bg-gradient-to-br from-metro-panel to-metro-panel/40 p-8 shadow-xl backdrop-blur ${styles.glow}`}
      aria-live="polite"
    >
      <div className="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full bg-metro-accent/5 blur-3xl" />

      <header className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-widest text-slate-500">
            Detalle de zona
          </p>
          <h2 className="mt-1 text-2xl font-semibold text-white">
            {formatVagonLabel(data.vagon_id)}
          </h2>
        </div>
        <span
          className={`inline-flex shrink-0 items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${styles.badge}`}
        >
          {styles.label}
        </span>
      </header>

      <p className="text-5xl font-bold tabular-nums tracking-tight text-white transition-all duration-500">
        {data.headcount}
        <span className="ml-2 text-xl font-medium text-slate-400">pasajeros</span>
      </p>

      <div className="mt-6">
        <div className="mb-2 flex justify-between text-xs text-slate-400">
          <span>Ocupación</span>
          <span>{occupancyPct}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-slate-800/80">
          <div
            className={`h-full rounded-full transition-all duration-700 ease-out ${styles.bar}`}
            style={{ width: `${occupancyPct}%` }}
          />
        </div>
      </div>

      <footer className="mt-6 flex items-center justify-between border-t border-metro-border/60 pt-4 text-xs text-slate-500">
        <span>
          {lastUpdated
            ? `Actualizado ${lastUpdated.toLocaleTimeString("es-CL")}`
            : "—"}
        </span>
        {refreshing && (
          <span className="text-metro-accent">Sincronizando…</span>
        )}
      </footer>
    </article>
  );
}
