"""Contratos JSON alineados con Tarea 1 (mock GET) y Tarea 4 (POST analyze)."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from status_rules import OccupationStatus, derive_status


class OccupationSnapshot(BaseModel):
    vagon_id: str
    headcount: int = Field(ge=0)
    status: OccupationStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    frame_index: int | None = None

    @classmethod
    def from_detection(
        cls,
        *,
        vagon_id: str,
        headcount: int,
        capacity: int,
        frame_index: int | None = None,
    ) -> OccupationSnapshot:
        return cls(
            vagon_id=vagon_id,
            headcount=headcount,
            status=derive_status(headcount, capacity),
            frame_index=frame_index,
        )

    def to_mock_dict(self) -> dict:
        """Shape compatible con GET /api/v1/occupation/{vagon_id} (Tarea 1)."""
        return {
            "vagon_id": self.vagon_id,
            "headcount": self.headcount,
            "status": self.status,
        }

    def to_analyze_dict(self) -> dict:
        """Shape compatible con POST /api/v1/analyze (Tarea 4 / arquitectura)."""
        return {
            "zone_id": self.vagon_id,
            "headcount": self.headcount,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
