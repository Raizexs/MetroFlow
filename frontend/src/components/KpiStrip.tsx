import type { OccupationResponse } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";

interface KpiStripProps {
  data: OccupationResponse;
}

export function KpiStrip({ data }: KpiStripProps) {
  const pct = Math.min(100, Math.round((data.headcount / VAGON_CAPACITY) * 100));

  const kpis = [
    {
      label: "Pasajeros detectados",
      value: String(data.headcount),
      sub: "conteo IA anonimizado",
      icon: (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
    },
    {
      label: "Ocupación",
      value: `${pct}%`,
      sub: `de ${VAGON_CAPACITY} plazas`,
      icon: (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      label: "Estado operativo",
      value:
        data.status === "normal"
          ? "Normal"
          : data.status === "warning"
            ? "Advertencia"
            : "Crítico",
      sub: "semáforo de aforo",
      icon: (
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="mb-8 grid gap-4 sm:grid-cols-3">
      {kpis.map((kpi) => (
        <div
          key={kpi.label}
          className="group rounded-2xl border border-metro-border/80 bg-metro-panel/60 p-5 backdrop-blur-sm transition hover:border-metro-accent/30"
        >
          <div className="mb-3 flex items-center justify-between text-metro-accent">
            {kpi.icon}
          </div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            {kpi.label}
          </p>
          <p className="mt-1 text-3xl font-bold tabular-nums text-white transition-all duration-300">
            {kpi.value}
          </p>
          <p className="mt-1 text-xs text-slate-500">{kpi.sub}</p>
        </div>
      ))}
    </div>
  );
}
