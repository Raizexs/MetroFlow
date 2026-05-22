/** Sincronizado con edge_ingestor push_interval (~6 s) durante detención del tren. */
export const DASHBOARD_POLL_MS = 6000;

export const DASHBOARD_POLL_LABEL = "cada 6 s";

/** Sin telemetría nueva (el tren partió): dejar de mostrar "en vivo". */
export const STALE_TELEMETRY_MS = DASHBOARD_POLL_MS * 2 + 4000;

export const LIVE_STATUS_LABEL = `En vivo · ${DASHBOARD_POLL_LABEL}`;
export const TRAIN_DEPARTED_LABEL = "Tren en ruta · sin detención activa";
