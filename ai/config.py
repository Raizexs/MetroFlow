"""Constantes compartidas del pipeline de inferencia (Tarea 3)."""

from pathlib import Path

MODEL_NAME = "yolo11m.pt"      # yolo11m para multitudes; alternativa yolov8n.pt
DEMO_FAST_MODEL = "yolo11n.pt"  # más rápido para --show / demo en vivo
PERSON_CLASS_ID = 0  # COCO: person
CONF_THRESHOLD = 0.4  # compromiso demo: plan 0.5 vs multitudes 0.25
DEMO_CONF_THRESHOLD = 0.4
INFER_IMGSZ = 1280
DEMO_FAST_IMGSZ = 960
DEMO_PLAYBACK_FPS = 30.0  # default genérico con --show
DEFAULT_EFE_PLAYBACK_FPS = 60.0  # ventana en vivo preset efe (fuente ~120 fps)

DEFAULT_VAGON_ID = "vagon_1"
DEFAULT_CAPACITY = 50
DEFAULT_SAMPLE_FPS = 2.0
# Intervalo entre POST al API (s); alineado con polling del dashboard (~6 s)
DEFAULT_PUSH_INTERVAL_SEC = 6.0

AI_DIR = Path(__file__).resolve().parent
VIDEOS_DIR = AI_DIR / "videos"
DEFAULT_EFE_VIDEO = VIDEOS_DIR / "efe-subway-arriving.mp4"
DEFAULT_VIDEO = VIDEOS_DIR / "sample.mp4"
DEFAULT_METRO_VIDEO = VIDEOS_DIR / "metro_entrada.mp4"
DEFAULT_DEMO_OUTPUT = VIDEOS_DIR / "metro_demo_salida.mp4"

# EFE: calibrado con calibrate_line.py (perspectiva, tren a la derecha)
DEFAULT_LINE = "385,557,672,779"
DEFAULT_EFE_LINE = DEFAULT_LINE
DEFAULT_INSIDE_POSITIVE = True
DEFAULT_INFER_EVERY = 4  # guardar MP4 con calidad
DEFAULT_INFER_EVERY_SHOW = 8  # demo en vivo (--show)
