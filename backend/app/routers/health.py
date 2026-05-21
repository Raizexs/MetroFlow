from fastapi import APIRouter

from app.schemas import StatusResponse

router = APIRouter(tags=["health"])


@router.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    return StatusResponse(status="ok")
