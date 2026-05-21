"""Configuración del backend mock (sincronizar capacidad con ai/config.py)."""

DEFAULT_CAPACITY = 50
DEFAULT_VAGON_ID = "vagon_1"

import os

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

_extra = os.getenv("CORS_EXTRA_ORIGIN")
if _extra:
    CORS_ORIGINS.append(_extra)
