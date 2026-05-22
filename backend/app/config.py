"""Configuración del backend mock (sincronizar capacidad con ai/config.py)."""

DEFAULT_CAPACITY = 50
DEFAULT_VAGON_ID = "vagon_1"

import os

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Producción Vercel: cualquier subdominio *.vercel.app (preview + production)
CORS_ORIGIN_REGEX = os.getenv(
    "CORS_ORIGIN_REGEX",
    r"https://[\w.-]+\.vercel\.app",
)


def _normalize_origin(value: str) -> str:
    return value.strip().rstrip("/")


def _parse_extra_origins() -> list[str]:
    raw = os.getenv("CORS_EXTRA_ORIGINS") or os.getenv("CORS_EXTRA_ORIGIN") or ""
    if not raw.strip():
        return []
    return [_normalize_origin(part) for part in raw.split(",") if part.strip()]


for origin in _parse_extra_origins():
    if origin not in CORS_ORIGINS:
        CORS_ORIGINS.append(origin)
