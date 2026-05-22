"""Presets de video y calibración para demos MetroFlow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import (
    AI_DIR,
    DEFAULT_EFE_PLAYBACK_FPS,
    DEMO_FAST_IMGSZ,
    DEMO_FAST_MODEL,
    INFER_IMGSZ,
    MODEL_NAME,
    VIDEOS_DIR,
)


@dataclass(frozen=True)
class VideoPreset:
    name: str
    video: Path
    line: str
    perspective: bool
    train_on_right: bool
    inside_positive: bool
    infer_every: int
    infer_every_show: int
    model: str
    imgsz: int
    conf: float
    playback_fps: float | None = None
    extra_lines: str | None = None
    sample_fps: float | None = None
    push_interval_sec: float | None = None
    demo_timeline: bool = False
    notes: str = ""


PRESETS: dict[str, VideoPreset] = {
    "efe": VideoPreset(
        name="efe",
        video=VIDEOS_DIR / "efe-subway-arriving.mp4",
        # Umbral puerta (calibrate_line.py): 385,557 → 672,779
        line="385,557,672,779",
        perspective=True,
        train_on_right=True,
        inside_positive=True,
        infer_every=4,
        infer_every_show=8,
        model=MODEL_NAME,
        imgsz=INFER_IMGSZ,
        conf=0.35,
        playback_fps=DEFAULT_EFE_PLAYBACK_FPS,
        extra_lines=None,
        sample_fps=0.2,
        push_interval_sec=6.0,
        demo_timeline=True,
        notes="EFE Biotren: demo aleatorio 20–40s en andén o --live para YOLO con línea.",
    ),
    "metro_entrada": VideoPreset(
        name="metro_entrada",
        video=VIDEOS_DIR / "metro_entrada.mp4",
        line="633,434,1233,435",
        perspective=False,
        train_on_right=True,
        inside_positive=True,
        infer_every=1,
        infer_every_show=2,
        model=DEMO_FAST_MODEL,
        imgsz=DEMO_FAST_IMGSZ,
        conf=0.4,
        notes="Mixkit: subida/salida andén exterior genérico.",
    ),
    "sample": VideoPreset(
        name="sample",
        video=VIDEOS_DIR / "sample.mp4",
        line="200,300,1000,300",
        perspective=False,
        train_on_right=True,
        inside_positive=True,
        infer_every=1,
        infer_every_show=2,
        model=DEMO_FAST_MODEL,
        imgsz=DEMO_FAST_IMGSZ,
        conf=0.4,
    ),
}


DEFAULT_PRESET_NAME = "efe"


def get_preset(name: str | None) -> VideoPreset | None:
    if not name:
        return None
    return PRESETS.get(name)


def resolve_default_video() -> Path:
    """Video por defecto: preset EFE si existe el archivo."""
    efe = PRESETS["efe"].video
    if efe.is_file():
        return efe
    metro = PRESETS["metro_entrada"].video
    if metro.is_file():
        return metro
    return PRESETS["sample"].video
