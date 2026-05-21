import type { ReactNode } from "react";

import { HelpModal } from "./HelpModal";

function LiveClock() {
  const now = new Date();
  const utc = now.toISOString().slice(11, 19);
  const local = now.toLocaleTimeString("es-CL");

  return (
    <div className="text-right text-xs text-slate-500">
      <p className="font-mono text-slate-400">{utc} UTC</p>
      <p>{local} local</p>
    </div>
  );
}

interface AppShellProps {
  children: ReactNode;
  apiOnline: boolean | null;
  activeSection?: string;
}

export function AppShell({ children, apiOnline, activeSection = "resumen" }: AppShellProps) {
  const nav = [
    { id: "resumen", label: "Resumen en vivo" },
    { id: "vagones", label: "Vagones" },
    { id: "legal", label: "Privacidad" },
  ];

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-56 shrink-0 flex-col border-r border-metro-border bg-metro-panel/50 lg:flex">
        <div className="border-b border-metro-border px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-metro-accent to-cyan-600 text-lg font-bold text-white shadow-lg shadow-sky-500/20">
              M
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-widest text-metro-accent">
                MetroFlow
              </p>
              <p className="text-sm font-semibold text-white">Control de aforo</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 p-4">
          {nav.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block rounded-lg px-3 py-2 text-sm transition ${
                activeSection === item.id
                  ? "bg-metro-accent/15 font-medium text-sky-300"
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>
        <p className="border-t border-metro-border p-4 text-[10px] leading-relaxed text-slate-600">
          Solo métricas anonimizadas. Sin video ni datos biométricos (Ley 21.719).
        </p>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 border-b border-metro-border bg-metro-bg/90 backdrop-blur-md">
          <div className="flex items-center justify-between gap-4 px-6 py-4">
            <div className="lg:hidden">
              <p className="text-xs font-medium uppercase tracking-widest text-metro-accent">
                MetroFlow
              </p>
              <h1 className="text-lg font-semibold text-white">Control de aforo</h1>
            </div>
            <p className="hidden text-sm text-slate-400 lg:block">
              Centro de operaciones · Monitoreo en tiempo real
            </p>
            <div className="flex items-center gap-4 sm:gap-6">
              <HelpModal />
              <LiveClock />
              <div className="flex items-center gap-2 rounded-full border border-metro-border bg-metro-panel px-3 py-1.5 text-xs">
                <span
                  className={`h-2 w-2 rounded-full ${
                    apiOnline === null
                      ? "animate-pulse bg-slate-500"
                      : apiOnline
                        ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"
                        : "bg-red-400"
                  }`}
                />
                API {apiOnline ? "en línea" : apiOnline === false ? "offline" : "…"}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 py-8 sm:px-6 lg:px-10">{children}</main>

        <footer
          id="legal"
          className="border-t border-metro-border bg-metro-panel/30 px-6 py-4 text-center text-xs text-slate-600"
        >
          Privacidad por diseño · Ley N° 21.719 (Chile). El sistema no almacena video ni
          identifica personas; solo transmite conteos agregados.
        </footer>
      </div>
    </div>
  );
}
