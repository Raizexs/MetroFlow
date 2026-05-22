/**
 * Parámetros del servicio EFE Biotren (Limache–Puerto Valparaíso)
 * para interpretar densidad en andén según frecuencia y detención típica.
 */

export interface EfeServiceContext {
  periodLabel: string;
  /** Minutos entre trenes (referencia principal para densidad en andén). */
  intervalMinutes: number;
  intervalNote: string;
  dwellLabel: string;
  isPeakWeekday: boolean;
}

/** Capacidad de referencia en zona de andén según intervalo entre trenes. */
export function efeReferenceCapacity(intervalMinutes: number): number {
  if (intervalMinutes <= 6) return 38;
  if (intervalMinutes <= 12) return 48;
  return 55;
}

export function getEfeServiceContext(now = new Date()): EfeServiceContext {
  const chile = new Date(
    now.toLocaleString("en-US", { timeZone: "America/Santiago" }),
  );
  const day = chile.getDay();
  const hour = chile.getHours();
  const minute = chile.getMinutes();
  const hm = hour + minute / 60;

  if (day === 0) {
    return {
      periodLabel: "Domingo o festivo",
      intervalMinutes: 15,
      intervalNote: "Aprox. cada 15 min (Puerto–Limache)",
      dwellLabel: "20–40 s en estación",
      isPeakWeekday: false,
    };
  }

  if (day === 6) {
    return {
      periodLabel: "Sábado",
      intervalMinutes: 12,
      intervalNote: "Aprox. cada 12 min",
      dwellLabel: "20–40 s en estación",
      isPeakWeekday: false,
    };
  }

  const morningPeak = hm >= 7 && hm < 9.5;
  const eveningPeak = hm >= 17 && hm < 20.5;
  const isPeak = morningPeak || eveningPeak;

  if (isPeak) {
    return {
      periodLabel: "Hora punta (lunes a viernes)",
      intervalMinutes: 6,
      intervalNote: "Puerto–Sargento Aldea ~6 min · tramo completo ~12 min",
      dwellLabel: "20–40 s (solo puertas y embarque)",
      isPeakWeekday: true,
    };
  }

  return {
    periodLabel: "Horario valle (lunes a viernes)",
    intervalMinutes: 13,
    intervalNote: "Aprox. cada 12 a 15 min",
    dwellLabel: "20–40 s en estación",
    isPeakWeekday: false,
  };
}

/** Porcentaje de densidad calibrado al intervalo EFE (no capacidad del vagón). */
export function efeDensityPercent(headcount: number, intervalMinutes: number): number {
  const ref = efeReferenceCapacity(intervalMinutes);
  return Math.min(100, Math.round((headcount / ref) * 100));
}

export function efeDensityLabel(pct: number): string {
  if (pct < 45) return "Baja para el intervalo actual";
  if (pct < 70) return "Moderada — dentro de lo esperable";
  if (pct < 88) return "Alta — conviene anticipar el próximo tren";
  return "Muy alta — posible congestión o demora del servicio";
}

/** Texto breve para operadores (español chileno). */
export const EFE_SERVICE_EXPLANATION = `El tren Limache–Puerto (EFE Valparaíso) no funciona como una micro en el paradero: sigue una frecuencia fija y en cada estación se detiene solo el tiempo necesario para abrir puertas, dejar subir y bajar pasajeros, cerrar y seguir — en general entre 20 y 40 segundos, un poco más en estaciones con mayor flujo (Viña del Mar, Quilpué, Villa Alemana, Puerto o Limache).

Entre semana en hora punta pasa aproximadamente cada 6 minutos en Puerto–Sargento Aldea y cada 12 minutos en el tramo completo hasta Limache. En valle suele ser cada 12 a 15 minutos; los sábados alrededor de 12 minutos; domingos y festivos cerca de 15 minutos. En estaciones intermedias no suele quedar detenido varios minutos, salvo congestión o incidentes.`;
