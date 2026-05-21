import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryPoint } from "../types/occupation";
import { VAGON_CAPACITY } from "../types/occupation";

interface OccupancyChartProps {
  points: HistoryPoint[];
}

export function OccupancyChart({ points }: OccupancyChartProps) {
  const chartData = points.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString("es-CL", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }),
    headcount: p.headcount,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl border border-metro-border bg-metro-panel/40 text-sm text-slate-500">
        Esperando datos de ocupación…
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-metro-border bg-metro-panel/40 p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Historial de ocupación
      </h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="time" tick={{ fill: "#64748b", fontSize: 10 }} tickLine={false} />
            <YAxis
              domain={[0, VAGON_CAPACITY]}
              tick={{ fill: "#64748b", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "#141c2f",
                border: "1px solid #243049",
                borderRadius: "8px",
                fontSize: "12px",
              }}
              labelStyle={{ color: "#94a3b8" }}
            />
            <Area
              type="monotone"
              dataKey="headcount"
              stroke="#38bdf8"
              strokeWidth={2}
              fill="url(#colorCount)"
              name="Pasajeros"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
