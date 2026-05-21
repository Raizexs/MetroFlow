import { useCallback, useEffect, useState } from "react";
import { fetchOccupation } from "../api/client";
import type { HistoryPoint, OccupationResponse } from "../types/occupation";

const POLL_INTERVAL_MS = 5000;

export function useOccupation(vagonId: string) {
  const [data, setData] = useState<OccupationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [historyBuffer, setHistoryBuffer] = useState<HistoryPoint[]>([]);

  const load = useCallback(
    async (isInitial: boolean) => {
      if (isInitial) setLoading(true);
      else setRefreshing(true);
      setError(null);

      try {
        const result = await fetchOccupation(vagonId);
        setData(result);
        setLastUpdated(new Date());
        setHistoryBuffer((prev) => {
          const point: HistoryPoint = {
            headcount: result.headcount,
            status: result.status,
            timestamp: new Date().toISOString(),
          };
          const next = [...prev, point].slice(-30);
          return next;
        });
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
    void load(true);
    const id = window.setInterval(() => void load(false), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  return { data, loading, refreshing, error, lastUpdated, historyBuffer };
}
