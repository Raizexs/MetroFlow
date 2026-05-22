/** Etiqueta legible para operadores (API sigue usando vagon_1). */
export function formatVagonLabel(vagonId: string): string {
  const match = vagonId.match(/vagon_(\d+)/i);
  if (match) return `Vagón ${match[1]}`;
  return vagonId.replace(/_/g, " ");
}
