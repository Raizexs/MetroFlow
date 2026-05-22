import { useCallback, useEffect, useState } from "react";
import { fetchOccupationHistory } from "../api/client";
import type { HistoryPoint } from "../types/occupation";

import { DASHBOARD_POLL_MS } from "../config/polling";

function mergeHistory(api: HistoryPoint[], local: HistoryPoint[]): HistoryPoint[] {
  const map = new Map<string, HistoryPoint>();
  for (const p of api) {
    map.set(p.timestamp, p);
  }
  for (const p of local) {
    map.set(p.timestamp, p);
  }
  return [...map.values()]
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .slice(-120);
}

export function useOccupationHistory(vagonId: string, localBuffer: HistoryPoint[]) {
  const [apiPoints, setApiPoints] = useState<HistoryPoint[]>([]);

  const load = useCallback(async () => {
    try {
      const res = await fetchOccupationHistory(vagonId, 120);
      setApiPoints(res.points);
    } catch {
      /* fallback al buffer local */
    }
  }, [vagonId]);

  useEffect(() => {
    void load();
    const id = window.setInterval(() => void load(), DASHBOARD_POLL_MS);
    return () => window.clearInterval(id);
  }, [load]);

  const points = mergeHistory(apiPoints, localBuffer);

  return { points };
}
