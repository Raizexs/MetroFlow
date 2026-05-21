import type { OccupationStatus } from "../types/occupation";

const COPY: Record<Exclude<OccupationStatus, "normal">, { title: string; body: string }> = {
  warning: {
    title: "Ocupación elevada",
    body: "El vagón se acerca al límite de capacidad. Considere redistribuir pasajeros.",
  },
  critical: {
    title: "Alerta crítica de aforo",
    body: "Capacidad casi superada. Active protocolo de contención en estación.",
  },
};

interface AlertBannerProps {
  status: OccupationStatus;
}

export function AlertBanner({ status }: AlertBannerProps) {
  if (status === "normal") return null;

  const isCritical = status === "critical";
  const content = COPY[status];

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={`mb-6 flex items-start gap-4 rounded-xl border px-5 py-4 ${
        isCritical
          ? "animate-pulse-slow border-red-500/50 bg-red-500/10"
          : "border-amber-500/40 bg-amber-500/10"
      }`}
    >
      <span
        className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-lg font-bold ${
          isCritical ? "bg-red-500 text-white" : "bg-amber-500 text-slate-900"
        }`}
      >
        !
      </span>
      <div>
        <p className={`font-semibold ${isCritical ? "text-red-200" : "text-amber-200"}`}>
          {content.title}
        </p>
        <p className="mt-1 text-sm text-slate-300">{content.body}</p>
      </div>
    </div>
  );
}
