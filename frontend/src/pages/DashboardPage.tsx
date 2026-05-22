import { useEffect, useRef } from "react";
import { useLocation, useOutletContext } from "react-router-dom";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { AlertBanner } from "../components/AlertBanner";
import { KpiStrip } from "../components/KpiStrip";
import { MetroSchematic } from "../components/MetroSchematic";
import { OccupancyChart } from "../components/OccupancyChart";
import { EfeScheduleStrip } from "../components/EfeScheduleStrip";
import { SystemPipeline } from "../components/SystemPipeline";
import { VagonCard } from "../components/VagonCard";
import { useOccupation } from "../hooks/useOccupation";
import { useOccupationHistory } from "../hooks/useOccupationHistory";
import { prefersReducedMotion } from "../lib/motion";

const VAGON_ID = "vagon_1";

type OutletCtx = { apiOnline: boolean | null };

export function DashboardPage() {
  const { apiOnline } = useOutletContext<OutletCtx>();
  const location = useLocation();
  const vagonRef = useRef<HTMLDivElement>(null);
  const pageRef = useRef<HTMLDivElement>(null);

  const {
    data,
    loading,
    refreshing,
    error,
    lastUpdated,
    lastTelemetryAt,
    telemetryActive,
    historyBuffer,
    delta,
  } = useOccupation(VAGON_ID);
  const { points: historyPoints } = useOccupationHistory(VAGON_ID, historyBuffer);

  useEffect(() => {
    if (location.pathname === "/vagones") {
      vagonRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [location.pathname]);

  useGSAP(
    () => {
      if (prefersReducedMotion() || !pageRef.current) return;
      gsap.from(".dash-reveal", {
        opacity: 0,
        y: 20,
        duration: 0.5,
        stagger: 0.06,
        ease: "power2.out",
      });
    },
    { scope: pageRef, dependencies: [loading] },
  );

  if (loading && !data) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-32 rounded-2xl bg-metro-panel" />
        <div className="grid gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 rounded-2xl bg-metro-panel" />
          ))}
        </div>
        <div className="h-72 rounded-2xl bg-metro-panel" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div ref={pageRef} className="space-y-8">
      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <SystemPipeline
        apiOnline={apiOnline}
        lastSync={lastUpdated}
        headcount={data.headcount}
        historyPoints={historyPoints}
        delta={delta}
        telemetryActive={telemetryActive}
      />

      <div className="dash-reveal">
        <AlertBanner status={data.status} />
      </div>

      <div className="dash-reveal">
        <EfeScheduleStrip />
      </div>

      <div className="dash-reveal">
        <KpiStrip data={data} delta={delta} />
      </div>

      <div className="grid gap-8 xl:grid-cols-3">
        <div className="dash-reveal xl:col-span-2">
          <MetroSchematic
            status={data.status}
            headcount={data.headcount}
            vagonId={data.vagon_id}
            delta={delta}
          />
        </div>
        <div ref={vagonRef} className="dash-reveal scroll-mt-24">
          <VagonCard
            data={data}
            refreshing={refreshing}
            lastUpdated={lastUpdated}
            lastTelemetryAt={lastTelemetryAt}
            telemetryActive={telemetryActive}
            delta={delta}
          />
        </div>
      </div>

      <div className="dash-reveal">
        <OccupancyChart
          points={historyPoints}
          liveHeadcount={data.headcount}
          telemetryActive={telemetryActive}
        />
      </div>
    </div>
  );
}
