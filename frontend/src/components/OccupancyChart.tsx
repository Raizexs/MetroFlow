import { useMemo, useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { DASHBOARD_POLL_LABEL, TRAIN_DEPARTED_LABEL } from "../config/polling";
import { prefersReducedMotion } from "../lib/motion";
import type { HistoryPoint } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";

interface OccupancyChartProps {
  points: HistoryPoint[];
  liveHeadcount: number;
  telemetryActive: boolean;
}

export function OccupancyChart({
  points,
  liveHeadcount,
  telemetryActive,
}: OccupancyChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  const chartData = useMemo(
    () =>
      points.map((p, i) => ({
        idx: i,
        time: new Date(p.timestamp).toLocaleTimeString("es-CL", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
        headcount: p.headcount,
        isLast: i === points.length - 1,
      })),
    [points],
  );

  useGSAP(
    () => {
      if (prefersReducedMotion() || !chartRef.current || chartData.length < 2) return;
      gsap.fromTo(
        chartRef.current,
        { opacity: 0.92 },
        { opacity: 1, duration: 0.25, ease: "power1.out" },
      );
    },
    { dependencies: [chartData.length, liveHeadcount], scope: chartRef },
  );

  if (chartData.length === 0) {
    return (
      <div className="flex h-72 items-center justify-center rounded-2xl border border-metro-border bg-metro-panel/40 text-sm text-slate-500">
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 animate-pulse rounded-full bg-sky-400" />
          Esperando telemetría del edge…
        </span>
      </div>
    );
  }

  return (
    <div
      ref={chartRef}
      className="rounded-2xl border border-metro-border/80 bg-gradient-to-b from-metro-panel/60 to-metro-panel/20 p-6 shadow-lg"
    >
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Línea continua de ocupación
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            {telemetryActive
              ? `Actualización ${DASHBOARD_POLL_LABEL} durante detención del tren`
              : "Historial de la última detención · el tren ya partió"}
          </p>
        </div>
        <div
          className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
            telemetryActive
              ? "border-sky-500/30 bg-sky-500/10 text-sky-200"
              : "border-slate-600/50 bg-slate-800/40 text-slate-400"
          }`}
        >
          {telemetryActive ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-50" />
                <span className="relative h-2 w-2 rounded-full bg-sky-400" />
              </span>
              En vivo · {liveHeadcount} pax
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-slate-500" />
              {TRAIN_DEPARTED_LABEL}
            </>
          )}
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 12, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: "#64748b", fontSize: 10 }}
              tickLine={false}
              minTickGap={28}
            />
            <YAxis
              domain={[0, VAGON_CAPACITY]}
              tick={{ fill: "#64748b", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                background: "#0c1222",
                border: "1px solid #1e3a5f",
                borderRadius: "10px",
                fontSize: "12px",
              }}
              labelStyle={{ color: "#94a3b8" }}
              formatter={(value: number) => [`${value} pasajeros`, "Ocupación"]}
            />
            <Line
              type="monotone"
              dataKey="headcount"
              stroke="#38bdf8"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 6, fill: "#7dd3fc", stroke: "#0ea5e9", strokeWidth: 2 }}
              isAnimationActive={!prefersReducedMotion()}
              animationDuration={400}
              animationEasing="ease-out"
              name="Pasajeros"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
