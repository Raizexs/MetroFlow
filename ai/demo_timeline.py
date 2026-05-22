"""
Demo EFE: ocupación aleatoria (sube/baja) durante la detención del tren en andén.
Ventana 20–40 s (hasta ~45 s en estación con mayor flujo), POST cada ~6 s.
"""

from __future__ import annotations

import random

# Tiempo hasta próximo tren (solo mensaje al terminar)
EFE_DEMO_COOLDOWN_SEC = 360.0

# Detención típica EFE: puertas abiertas, suben/bajan, cierran y siguen
DWELL_NORMAL_MIN_SEC = 20.0
DWELL_NORMAL_MAX_SEC = 40.0
DWELL_BUSY_MIN_SEC = 30.0
DWELL_BUSY_MAX_SEC = 45.0
BUSY_STATION_CHANCE = 0.35

HEADCOUNT_MIN = 0
HEADCOUNT_START_MIN = 8
HEADCOUNT_START_MAX = 22


def random_dwell_seconds(rng: random.Random) -> tuple[float, bool]:
    """Duración de detención y si se modela estación de mayor flujo."""
    busy = rng.random() < BUSY_STATION_CHANCE
    if busy:
        return rng.uniform(DWELL_BUSY_MIN_SEC, DWELL_BUSY_MAX_SEC), True
    return rng.uniform(DWELL_NORMAL_MIN_SEC, DWELL_NORMAL_MAX_SEC), False


def generate_random_dwell_schedule(
    push_interval_sec: float,
    *,
    capacity: int = 50,
    seed: int | None = None,
) -> tuple[list[tuple[float, int]], float, bool]:
    """
    Genera (tiempo, headcount) con variaciones aleatorias incrementales/decrementales.
    """
    rng = random.Random(seed)
    dwell_sec, busy_station = random_dwell_seconds(rng)
    headcount = rng.randint(HEADCOUNT_START_MIN, HEADCOUNT_START_MAX)
    schedule: list[tuple[float, int]] = [(0.0, headcount)]

    t = 0.0
    while t + push_interval_sec <= dwell_sec + 0.01:
        t += push_interval_sec
        # Mezcla de subidas, bajadas y pasos neutros (abordaje/desborde aleatorio)
        roll = rng.random()
        if roll < 0.4:
            delta = rng.randint(1, 14)
        elif roll < 0.8:
            delta = rng.randint(-12, -1)
        else:
            delta = rng.randint(-5, 8)

        headcount = max(HEADCOUNT_MIN, min(capacity, headcount + delta))
        schedule.append((round(t, 1), headcount))

    return schedule, dwell_sec, busy_station


def demo_push_schedule(
    push_interval_sec: float,
    *,
    capacity: int = 50,
    seed: int | None = None,
) -> list[tuple[float, int]]:
    """Compat: devuelve solo la lista de POST."""
    schedule, _, _ = generate_random_dwell_schedule(
        push_interval_sec, capacity=capacity, seed=seed
    )
    return schedule
