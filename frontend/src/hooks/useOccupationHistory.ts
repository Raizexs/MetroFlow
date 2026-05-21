import { useCallback, useEffect, useState } from "react";
import { fetchOccupationHistory } from "../api/client";
import type { HistoryPoint } from "../types/occupation";

const POLL_INTERVAL_MS = 10000;

export function useOccupationHistory(vagonId: string, localBuffer: HistoryPoint[]) {
  const [apiPoints, setApiPoints] = useState<HistoryPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await fetchOccupationHistory(vagonId);
      setApiPoints(res.points);
      setError(null);
    } catch {
      setError(null);
    }
  }, [vagonId]);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), POLL_INTERVAL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  const merged =
    apiPoints.length > 0
      ? apiPoints
      : localBuffer.map((p) => ({
          headcount: p.headcount,
          status: p.status,
          timestamp: p.timestamp,
        }));

  return { points: merged, error };
}
