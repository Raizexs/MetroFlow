import { useEffect, useState } from "react";

const ACTS = [
  {
    title: "1. Captura",
    body: "La cámara o el video se analizan en el equipo de estación con IA (YOLO). No hay video en este panel.",
  },
  {
    title: "2. Telemetría",
    body: "Solo números anonimizados se envían al servidor en la nube (API Render).",
  },
  {
    title: "3. Operación",
    body: "Este panel consulta el servidor cada 5 segundos y muestra conteo, gráfico y alertas.",
  },
] as const;

export function HelpModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg border border-metro-border bg-metro-panel px-3 py-1.5 text-xs font-medium text-sky-300 transition hover:border-sky-500/50 hover:bg-sky-950/30"
      >
        ¿Cómo funciona?
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="help-title"
          onClick={() => setOpen(false)}
        >
          <div
            className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-metro-border bg-metro-panel p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <h2 id="help-title" className="text-lg font-semibold text-white">
                  Cómo funciona el sistema
                </h2>
                <p className="mt-1 text-sm text-slate-400">
                  Tres actos — sin instalar software en su PC
                </p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-800 hover:text-white"
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            <ol className="space-y-4">
              {ACTS.map((act) => (
                <li
                  key={act.title}
                  className="rounded-xl border border-metro-border bg-metro-bg/60 p-4"
                >
                  <p className="text-sm font-semibold text-sky-300">{act.title}</p>
                  <p className="mt-1 text-sm leading-relaxed text-slate-300">{act.body}</p>
                </li>
              ))}
            </ol>

            <p className="mt-4 text-xs leading-relaxed text-slate-500">
              Privacidad (Ley 21.719): no se muestran imágenes de pasajeros. Solo métricas de
              aforo. Documentación: docs/GUIA_OPERADOR.md
            </p>
          </div>
        </div>
      )}
    </>
  );
}
