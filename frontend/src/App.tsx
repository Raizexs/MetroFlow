import { useEffect, useState } from "react";
import { fetchStatus } from "./api/client";
import { AlertBanner } from "./components/AlertBanner";
import { AppShell } from "./components/AppShell";
import { KpiStrip } from "./components/KpiStrip";
import { MetroSchematic } from "./components/MetroSchematic";
import { OccupancyChart } from "./components/OccupancyChart";
import { VagonCard } from "./components/VagonCard";
import { useOccupation } from "./hooks/useOccupation";
import { useOccupationHistory } from "./hooks/useOccupationHistory";

const VAGON_ID = "vagon_1";

export default function App() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const { data, loading, refreshing, error, lastUpdated, historyBuffer } =
    useOccupation(VAGON_ID);
  const { points: historyPoints } = useOccupationHistory(VAGON_ID, historyBuffer);

  useEffect(() => {
    fetchStatus()
      .then(() => {
        setApiOnline(true);
        setApiError(null);
      })
      .catch(() => {
        setApiOnline(false);
        setApiError(
          "No se pudo conectar al backend. Ejecuta: uvicorn app.main:app --port 8000",
        );
      });
  }, []);

  return (
    <AppShell apiOnline={apiOnline}>
      {apiError && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {apiError}
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {loading && !data ? (
        <div className="space-y-6 animate-pulse">
          <div className="grid gap-4 sm:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-28 rounded-2xl bg-metro-panel" />
            ))}
          </div>
          <div className="h-64 rounded-2xl bg-metro-panel" />
        </div>
      ) : data ? (
        <div id="resumen" className="space-y-8">
          <AlertBanner status={data.status} />
          <KpiStrip data={data} />
          <div className="grid gap-8 xl:grid-cols-3">
            <div className="xl:col-span-2">
              <MetroSchematic
                status={data.status}
                headcount={data.headcount}
                vagonId={data.vagon_id}
              />
            </div>
            <div id="vagones">
              <VagonCard
                data={data}
                refreshing={refreshing}
                lastUpdated={lastUpdated}
              />
            </div>
          </div>
          <OccupancyChart points={historyPoints} />
        </div>
      ) : null}
    </AppShell>
  );
}
