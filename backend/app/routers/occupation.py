from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app import database
from app.repository import fetch_history, insert_occupation
from app.schemas import (
    AnalyzePayload,
    HistoryPoint,
    OccupationHistoryResponse,
    OccupationResponse,
)
from app.store import store

router = APIRouter(tags=["occupation"])


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


async def _persist_and_update(payload: AnalyzePayload) -> OccupationResponse:
    snapshot = store.update(
        vagon_id=payload.zone_id,
        headcount=payload.headcount,
        status=payload.status,
    )

    if database.db_enabled and database.async_session_factory:
        async with database.async_session_factory() as session:
            await insert_occupation(
                session,
                zone_id=payload.zone_id,
                headcount=snapshot.headcount,
                status=snapshot.status,
                timestamp=_parse_timestamp(payload.timestamp),
            )

    return snapshot


@router.get("/occupation/{vagon_id}", response_model=OccupationResponse)
def get_occupation(vagon_id: str) -> OccupationResponse:
    snapshot = store.get(vagon_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail=f"Vagón '{vagon_id}' no encontrado")
    return snapshot


@router.get("/occupation/{vagon_id}/history", response_model=OccupationHistoryResponse)
async def get_occupation_history(vagon_id: str, limit: int = 60) -> OccupationHistoryResponse:
    limit = min(max(1, limit), 200)

    if database.db_enabled and database.async_session_factory:
        async with database.async_session_factory() as session:
            points = await fetch_history(session, vagon_id, limit)
            if points:
                return OccupationHistoryResponse(vagon_id=vagon_id, points=points)

    current = store.get(vagon_id)
    if current is None:
        raise HTTPException(status_code=404, detail=f"Vagón '{vagon_id}' no encontrado")

    return OccupationHistoryResponse(
        vagon_id=vagon_id,
        points=[
            HistoryPoint(
                headcount=current.headcount,
                status=current.status,
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
        ],
    )


@router.post("/analyze", response_model=OccupationResponse)
async def post_analyze(payload: AnalyzePayload) -> OccupationResponse:
    return await _persist_and_update(payload)


@router.post("/analyze/camera/{zone_id}", response_model=OccupationResponse)
async def post_analyze_camera(zone_id: str, payload: AnalyzePayload) -> OccupationResponse:
    """Endpoint documentado: /api/v1/analyze/camera/{id_espacio}."""
    payload.zone_id = zone_id
    return await _persist_and_update(payload)
