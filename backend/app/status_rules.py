"""Reglas de semáforo — mantener sincronizado con ai/status_rules.py."""

from typing import Literal

OccupationStatus = Literal["normal", "warning", "critical"]


def derive_status(headcount: int, capacity: int) -> OccupationStatus:
    if capacity <= 0:
        return "normal"

    ratio = headcount / capacity
    if ratio < 0.7:
        return "normal"
    if ratio <= 0.9:
        return "warning"
    return "critical"
