"""Modelos Pydantic — espejo de ai/schemas.py OccupationSnapshot.to_mock_dict()."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

OccupationStatusLiteral = Literal["normal", "warning", "critical"]


class OccupationResponse(BaseModel):
    vagon_id: str
    headcount: int = Field(ge=0)
    status: OccupationStatusLiteral


class StatusResponse(BaseModel):
    status: str = "ok"


class AnalyzePayload(BaseModel):
    """Body alineado con ai/schemas.py OccupationSnapshot.to_analyze_dict()."""

    zone_id: str
    headcount: int = Field(ge=0)
    status: Optional[OccupationStatusLiteral] = None
    timestamp: Optional[str] = None


class HistoryPoint(BaseModel):
    headcount: int
    status: OccupationStatusLiteral
    timestamp: str


class OccupationHistoryResponse(BaseModel):
    vagon_id: str
    points: List[HistoryPoint]
