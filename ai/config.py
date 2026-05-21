"""Constantes compartidas del pipeline de inferencia (Tarea 3)."""

from pathlib import Path

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS_ID = 0  # COCO: person
CONF_THRESHOLD = 0.5

DEFAULT_VAGON_ID = "vagon_1"
DEFAULT_CAPACITY = 50
DEFAULT_SAMPLE_FPS = 2.0

AI_DIR = Path(__file__).resolve().parent
DEFAULT_VIDEO = AI_DIR / "videos" / "sample.mp4"
