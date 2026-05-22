import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { HelpModal } from "./HelpModal";

function LiveClock() {
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

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
  apiOnline: boolean | null;
}

const NAV = [
  { to: "/", label: "Resumen en vivo", end: true },
  { to: "/vagones", label: "Vagones", end: false },
  { to: "/privacidad", label: "Privacidad", end: false },
] as const;

export function AppShell({ apiOnline }: AppShellProps) {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-metro-border bg-metro-panel/40 lg:flex">
        <div className="border-b border-metro-border px-5 py-6">
          <div className="flex items-center gap-3">
            <div className="logo-mark flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-sky-400 to-cyan-600 font-display text-lg font-bold text-white shadow-lg shadow-sky-500/25">
              M
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-sky-400">
                MetroFlow
              </p>
              <p className="font-display text-sm font-semibold text-white">Control de aforo</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 p-4">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2.5 text-sm transition ${
                  isActive
                    ? "bg-sky-500/15 font-medium text-sky-200 ring-1 ring-sky-500/25"
                    : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <p className="border-t border-metro-border p-4 text-[10px] leading-relaxed text-slate-600">
          Solo métricas anonimizadas. Sin video ni datos biométricos (Ley 21.719).
        </p>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 border-b border-metro-border/80 bg-metro-bg/85 backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6">
            <div className="lg:hidden">
              <p className="text-[10px] font-bold uppercase tracking-widest text-sky-400">
                MetroFlow
              </p>
              <h1 className="font-display text-lg font-semibold text-white">Control de aforo</h1>
            </div>
            <p className="hidden text-sm text-slate-400 lg:block">
              Centro de operaciones ·{" "}
              <span className="text-slate-300">Monitoreo continuo</span>
            </p>
            <div className="flex items-center gap-3 sm:gap-5">
              <nav className="flex gap-1 lg:hidden">
                {NAV.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={({ isActive }) =>
                      `rounded-md px-2 py-1 text-xs ${
                        isActive ? "bg-sky-500/20 text-sky-200" : "text-slate-500"
                      }`
                    }
                  >
                    {item.label.split(" ")[0]}
                  </NavLink>
                ))}
              </nav>
              <HelpModal />
              <LiveClock />
              <div className="flex items-center gap-2 rounded-full border border-metro-border bg-metro-panel/80 px-3 py-1.5 text-xs">
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

        <main className="page-enter flex-1 px-4 py-8 sm:px-6 lg:px-10">
          <Outlet context={{ apiOnline }} />
        </main>
      </div>
    </div>
  );
}
