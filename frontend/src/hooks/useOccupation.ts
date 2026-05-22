import { useCallback, useEffect, useRef, useState } from "react";
import { fetchOccupation } from "../api/client";
import { DASHBOARD_POLL_MS, STALE_TELEMETRY_MS } from "../config/polling";
import type { HistoryPoint, OccupationResponse } from "../types/occupation";

function snapshotKey(data: OccupationResponse): string {
  return `${data.headcount}:${data.status}`;
}

export function useOccupation(vagonId: string) {
  const [data, setData] = useState<OccupationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [lastTelemetryAt, setLastTelemetryAt] = useState<Date | null>(null);
  const [telemetryActive, setTelemetryActive] = useState(false);
  const [historyBuffer, setHistoryBuffer] = useState<HistoryPoint[]>([]);
  const [delta, setDelta] = useState(0);
  const prevHeadcount = useRef<number | null>(null);
  const prevSnapshot = useRef<string | null>(null);

  const load = useCallback(
    async (isInitial: boolean) => {
      if (isInitial) setLoading(true);
      else setRefreshing(true);
      setError(null);

      try {
        const result = await fetchOccupation(vagonId);
        const key = snapshotKey(result);
        const changed = prevSnapshot.current !== key;

        if (changed) {
          if (prevHeadcount.current !== null) {
            setDelta(result.headcount - prevHeadcount.current);
          }
          setLastTelemetryAt(new Date());
          setHistoryBuffer((prev) => {
            const point: HistoryPoint = {
              headcount: result.headcount,
              status: result.status,
              timestamp: new Date().toISOString(),
            };
            return [...prev, point].slice(-120);
          });
        } else {
          setDelta(0);
        }

        prevSnapshot.current = key;
        prevHeadcount.current = result.headcount;
        setData(result);
        setLastUpdated(new Date());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar ocupación");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [vagonId],
  );

  useEffect(() => {
    const evaluate = () => {
      if (!lastTelemetryAt) {
        setTelemetryActive(false);
        return;
      }
      setTelemetryActive(Date.now() - lastTelemetryAt.getTime() < STALE_TELEMETRY_MS);
    };
    evaluate();
    const id = window.setInterval(evaluate, 1000);
    return () => window.clearInterval(id);
  }, [lastTelemetryAt]);

  useEffect(() => {
    void load(true);
    const id = window.setInterval(() => void load(false), DASHBOARD_POLL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  return {
    data,
    loading,
    refreshing,
    error,
    lastUpdated,
    lastTelemetryAt,
    telemetryActive,
    historyBuffer,
    delta,
  };
}
