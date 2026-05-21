"""Reglas de semáforo de ocupación (alineadas con alertas del dashboard)."""

from typing import Literal

OccupationStatus = Literal["normal", "warning", "critical"]


def derive_status(headcount: int, capacity: int) -> OccupationStatus:
    """Deriva status según porcentaje de capacidad del vagón."""
    if capacity <= 0:
        return "normal"

    ratio = headcount / capacity
    if ratio < 0.7:
        return "normal"
    if ratio <= 0.9:
        return "warning"
    return "critical"
