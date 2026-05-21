"""Estado de ocupación en memoria (RAM volátil, sin persistencia)."""

from __future__ import annotations

from app.config import DEFAULT_CAPACITY, DEFAULT_VAGON_ID
from app.schemas import OccupationResponse
from app.status_rules import OccupationStatus, derive_status


class InMemoryStore:
    def __init__(self) -> None:
        self._capacity = DEFAULT_CAPACITY
        self._data: dict[str, OccupationResponse] = {
            DEFAULT_VAGON_ID: OccupationResponse(
                vagon_id=DEFAULT_VAGON_ID,
                headcount=15,
                status="normal",
            ),
        }

    def get(self, vagon_id: str) -> OccupationResponse | None:
        return self._data.get(vagon_id)

    def update(
        self,
        vagon_id: str,
        headcount: int,
        status: OccupationStatus | None = None,
    ) -> OccupationResponse:
        resolved_status: OccupationStatus = status or derive_status(
            headcount, self._capacity
        )
        snapshot = OccupationResponse(
            vagon_id=vagon_id,
            headcount=headcount,
            status=resolved_status,
        )
        self._data[vagon_id] = snapshot
        return snapshot


store = InMemoryStore()
