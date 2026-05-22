import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { useAnimatedValue } from "../hooks/useAnimatedValue";
import type { OccupationResponse } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";
import { prefersReducedMotion } from "../lib/motion";

interface KpiStripProps {
  data: OccupationResponse;
  delta?: number;
}

export function KpiStrip({ data, delta = 0 }: KpiStripProps) {
  const animatedCount = useAnimatedValue(data.headcount);
  const pct = Math.min(100, Math.round((data.headcount / VAGON_CAPACITY) * 100));
  const stripRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (prefersReducedMotion() || delta === 0 || !stripRef.current) return;
      gsap.fromTo(
        stripRef.current,
        { boxShadow: "0 0 0 rgba(14,165,233,0)" },
        {
          boxShadow: "0 0 28px rgba(14,165,233,0.35)",
          duration: 0.35,
          yoyo: true,
          repeat: 1,
        },
      );
    },
    { dependencies: [delta], scope: stripRef },
  );

  const kpis = [
    {
      label: "Pasajeros en zona",
      value: String(animatedCount),
      sub: delta !== 0 ? `${delta > 0 ? "+" : ""}${delta} última lectura` : "conteo IA anonimizado",
      icon: "users",
    },
    {
      label: "Ocupación",
      value: `${pct}%`,
      sub: `de ${VAGON_CAPACITY} plazas`,
      icon: "chart",
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
      icon: "shield",
    },
  ];

  return (
    <div ref={stripRef} className="grid gap-4 sm:grid-cols-3">
      {kpis.map((kpi) => (
        <div
          key={kpi.label}
          className="group rounded-2xl border border-metro-border/80 bg-gradient-to-br from-metro-panel/80 to-metro-panel/30 p-5 shadow-lg backdrop-blur-sm transition hover:border-sky-500/25"
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {kpi.label}
          </p>
          <p className="mt-2 font-display text-4xl font-bold tabular-nums tracking-tight text-white">
            {kpi.value}
          </p>
          <p className="mt-1 text-xs text-slate-500">{kpi.sub}</p>
        </div>
      ))}
    </div>
  );
}
