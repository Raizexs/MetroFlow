from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OcupacionRecord
from app.schemas import HistoryPoint, OccupationResponse


async def insert_occupation(
    session: AsyncSession,
    *,
    zone_id: str,
    headcount: int,
    status: str,
    timestamp: datetime | None = None,
) -> OcupacionRecord:
    ts = timestamp or datetime.now(timezone.utc)
    row = OcupacionRecord(
        zone_id=zone_id,
        headcount=headcount,
        status=status,
        timestamp=ts,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def fetch_history(
    session: AsyncSession,
    zone_id: str,
    limit: int = 60,
) -> list[HistoryPoint]:
    stmt = (
        select(OcupacionRecord)
        .where(OcupacionRecord.zone_id == zone_id)
        .order_by(OcupacionRecord.timestamp.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    rows.reverse()
    return [
        HistoryPoint(
            headcount=r.headcount,
            status=r.status,  # type: ignore[arg-type]
            timestamp=r.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        for r in rows
    ]


def to_occupation_response(zone_id: str, headcount: int, status: str) -> OccupationResponse:
    return OccupationResponse(vagon_id=zone_id, headcount=headcount, status=status)  # type: ignore[arg-type]
