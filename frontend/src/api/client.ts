// Capa SaaS: único cliente HTTP hacia el PaaS. Sin lógica de IA ni SQL.

import type {
  OccupationHistoryResponse,
  OccupationResponse,
  StatusResponse,
} from "../types/occupation";

function normalizeApiBase(raw: string | undefined): string {
  const base = (raw ?? "http://localhost:8000").trim();
  return base.replace(/\/+$/, "");
}

const API_URL = normalizeApiBase(import.meta.env.VITE_API_URL);

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Error HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchStatus(): Promise<StatusResponse> {
  const response = await fetch(`${API_URL}/api/v1/status`);
  return handleResponse<StatusResponse>(response);
}

export async function fetchOccupation(vagonId: string): Promise<OccupationResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/occupation/${encodeURIComponent(vagonId)}`,
  );
  return handleResponse<OccupationResponse>(response);
}

export async function fetchOccupationHistory(
  vagonId: string,
  limit = 60,
): Promise<OccupationHistoryResponse> {
  const response = await fetch(
    `${API_URL}/api/v1/occupation/${encodeURIComponent(vagonId)}/history?limit=${limit}`,
  );
  return handleResponse<OccupationHistoryResponse>(response);
}

export { API_URL };
