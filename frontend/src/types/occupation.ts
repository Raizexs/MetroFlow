/** Contrato alineado con backend y ai/schemas.py */

export type OccupationStatus = "normal" | "warning" | "critical";

export interface OccupationResponse {
  vagon_id: string;
  headcount: number;
  status: OccupationStatus;
}

export interface StatusResponse {
  status: string;
}

export interface HistoryPoint {
  headcount: number;
  status: OccupationStatus;
  timestamp: string;
}

export interface OccupationHistoryResponse {
  vagon_id: string;
  points: HistoryPoint[];
}

export const VAGON_CAPACITY = 50;
