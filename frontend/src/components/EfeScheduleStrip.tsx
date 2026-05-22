import { useMemo } from "react";

import {
  EFE_SERVICE_EXPLANATION,
  getEfeServiceContext,
} from "../lib/efeSchedule";

export function EfeScheduleStrip() {
  const ctx = useMemo(() => getEfeServiceContext(), []);

  return (
    <details className="group rounded-xl border border-metro-border/70 bg-metro-panel/40">
      <summary className="cursor-pointer list-none px-4 py-3 text-sm font-medium text-slate-300 marker:content-none [&::-webkit-details-marker]:hidden">
        <span className="flex flex-wrap items-center gap-2">
          <span className="rounded-md bg-sky-500/15 px-2 py-0.5 text-xs font-semibold text-sky-300">
            EFE Biotren
          </span>
          <span>{ctx.periodLabel}</span>
          <span className="text-slate-500">· cada ~{ctx.intervalMinutes} min</span>
          <span className="ml-auto text-xs text-sky-400/80 group-open:hidden">
            Ver frecuencia y detención
          </span>
        </span>
      </summary>
      <div className="border-t border-metro-border/60 px-4 py-4 text-sm leading-relaxed text-slate-400">
        <p>{EFE_SERVICE_EXPLANATION}</p>
        <ul className="mt-3 grid gap-2 text-xs text-slate-500 sm:grid-cols-2">
          <li>
            <strong className="text-slate-400">Frecuencia ahora:</strong> {ctx.intervalNote}
          </li>
          <li>
            <strong className="text-slate-400">Detención típica:</strong> {ctx.dwellLabel}
          </li>
        </ul>
        <p className="mt-3 text-xs text-slate-600">
          La densidad del panel se calcula respecto a cuántas personas cabrían esperar razonablemente
          en el andén antes del próximo tren, según ese intervalo.
        </p>
      </div>
    </details>
  );
}
