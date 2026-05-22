/** Respeta preferencia del sistema; evita animaciones costosas si el usuario lo pide. */
export function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
