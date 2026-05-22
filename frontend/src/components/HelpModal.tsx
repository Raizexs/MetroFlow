import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";

import { EFE_SERVICE_EXPLANATION } from "../lib/efeSchedule";
import { prefersReducedMotion } from "../lib/motion";

const STEPS = [
  {
    step: "01",
    title: "Captura e inferencia (Edge)",
    body: "Cámara o video en estación. YOLO11 + ByteTrack detectan personas; una línea virtual cuenta entradas y ocupación en zona. El video no sale del equipo.",
    accent: "border-violet-500/40 bg-violet-500/10",
  },
  {
    step: "02",
    title: "Telemetría (PaaS)",
    body: "edge_ingestor envía JSON ligero (headcount, estado) a FastAPI en Render. PostgreSQL guarda historial; sin imágenes ni identidad.",
    accent: "border-sky-500/40 bg-sky-500/10",
  },
  {
    step: "03",
    title: "Operación (SaaS)",
    body: "Este panel consulta la API cada ~6 s. En demo EFE, el ingestor simula subidas y bajadas aleatorias mientras el tren está detenido (20–40 s, puertas abiertas) y deja de enviar datos cuando el tren sigue.",
    accent: "border-emerald-500/40 bg-emerald-500/10",
  },
] as const;

export function HelpModal() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  useGSAP(
    () => {
      if (!open || !panelRef.current || !backdropRef.current) return;
      if (prefersReducedMotion()) return;
      gsap.fromTo(backdropRef.current, { opacity: 0 }, { opacity: 1, duration: 0.25 });
      gsap.fromTo(
        panelRef.current,
        { opacity: 0, y: 24, scale: 0.97 },
        { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "power3.out" },
      );
      gsap.from(".help-step", {
        opacity: 0,
        y: 16,
        stagger: 0.1,
        duration: 0.35,
        delay: 0.12,
        ease: "power2.out",
      });
    },
    { dependencies: [open], scope: panelRef },
  );

  const modal = open ? (
    <div
      ref={backdropRef}
      className="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/85 p-4 backdrop-blur-md"
      role="presentation"
      onClick={() => setOpen(false)}
    >
      <div
        ref={panelRef}
        className="help-panel max-h-[min(90vh,720px)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-metro-border bg-metro-panel p-6 shadow-2xl shadow-sky-950/40 sm:p-8"
        role="dialog"
        aria-modal="true"
        aria-labelledby="help-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">
              MetroFlow
            </p>
            <h2 id="help-title" className="font-display mt-1 text-2xl font-semibold text-white">
              Cómo funciona el sistema
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Tres capas conectadas: IA en borde, API en la nube y panel del operador.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setOpen(false)}
            className="shrink-0 rounded-lg border border-metro-border px-3 py-1.5 text-sm text-slate-400 transition hover:border-slate-500 hover:text-white"
            aria-label="Cerrar"
          >
            Cerrar
          </button>
        </div>

        <div className="mb-6 flex items-center justify-between gap-2 rounded-xl border border-metro-border/80 bg-metro-bg/50 px-4 py-3 text-xs text-slate-500">
          <span className="rounded-md bg-violet-500/20 px-2 py-1 font-medium text-violet-200">
            Edge
          </span>
          <span className="text-slate-600">→</span>
          <span className="rounded-md bg-sky-500/20 px-2 py-1 font-medium text-sky-200">
            Render API
          </span>
          <span className="text-slate-600">→</span>
          <span className="rounded-md bg-emerald-500/20 px-2 py-1 font-medium text-emerald-200">
            Vercel
          </span>
        </div>

        <ol className="space-y-4">
          {STEPS.map((item) => (
            <li
              key={item.step}
              className={`help-step rounded-xl border p-4 ${item.accent}`}
            >
              <p className="font-mono text-xs text-slate-500">{item.step}</p>
              <p className="mt-1 font-display text-base font-semibold text-white">
                {item.title}
              </p>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">{item.body}</p>
            </li>
          ))}
        </ol>

        <div className="help-step mt-6 rounded-xl border border-amber-500/25 bg-amber-500/5 p-4">
          <p className="font-display text-sm font-semibold text-amber-100/90">
            Servicio EFE Biotren (Limache–Puerto)
          </p>
          <p className="mt-2 text-sm leading-relaxed text-slate-400">
            {EFE_SERVICE_EXPLANATION}
          </p>
        </div>

        <p className="mt-6 text-xs leading-relaxed text-slate-500">
          Privacidad (Ley 21.719): solo métricas agregadas. Demo en vivo:{" "}
          <code className="rounded bg-metro-bg px-1 py-0.5 text-sky-300/90">
            python edge_ingestor.py --api &lt;URL Render&gt; --preset efe
          </code>
        </p>
      </div>
    </div>
  ) : null;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg border border-metro-border bg-metro-panel px-3 py-1.5 text-xs font-medium text-sky-300 transition hover:border-sky-500/50 hover:bg-sky-950/40"
      >
        ¿Cómo funciona?
      </button>
      {typeof document !== "undefined" ? createPortal(modal, document.body) : null}
    </>
  );
}
