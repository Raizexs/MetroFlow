"""
Conteo de personas en multitudes con YOLOv8n.
Inferencia headless a alta resolución (imgsz=1280) para mitigar oclusión.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ultralytics import YOLO

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS = 0
CONFIDENCE = 0.25
IOU_THRESH = 0.7
INPUT_SIZE = 1280


def analyze_crowd(image_path: str) -> dict:
    """
    Procesa una imagen y retorna el conteo de personas detectadas.

    Args:
        image_path: Ruta absoluta o relativa a la imagen.

    Returns:
        dict con {"status": "success", "headcount": int}
        o {"status": "error", "message": str} en caso de fallo.
    """
    try:
        path = Path(image_path)
        if not path.is_file():
            return {"status": "error", "message": f"Archivo no encontrado: {image_path}"}

        model = YOLO(MODEL_NAME)

        results = model(
            str(path),
            imgsz=INPUT_SIZE,
            conf=CONFIDENCE,
            iou=IOU_THRESH,
            classes=[PERSON_CLASS],
            verbose=False,
        )

        boxes = results[0].boxes
        headcount = len(boxes) if boxes is not None else 0

        return {"status": "success", "headcount": headcount}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python crowd_counter.py <ruta_de_imagen>")
        return 1

    result = analyze_crowd(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
