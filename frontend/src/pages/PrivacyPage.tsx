export function PrivacyPage() {
  return (
    <article className="mx-auto max-w-2xl space-y-6">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-400">
          Cumplimiento
        </p>
        <h1 className="font-display mt-2 text-3xl font-semibold text-white">Privacidad</h1>
      </header>
      <div className="space-y-4 rounded-2xl border border-metro-border bg-metro-panel/50 p-6 text-sm leading-relaxed text-slate-300">
        <p>
          MetroFlow opera bajo <strong className="text-white">privacidad por diseño</strong> (Ley
          N° 21.719, Chile). El sistema no almacena video en la nube ni identifica personas.
        </p>
        <ul className="list-inside list-disc space-y-2 text-slate-400">
          <li>Inferencia de IA en el borde (estación / edge).</li>
          <li>Solo se transmiten conteos agregados y estado de aforo.</li>
          <li>El panel SaaS muestra métricas operativas, no imágenes de pasajeros.</li>
        </ul>
      </div>
    </article>
  );
}
