"""
Conteo de personas en multitudes extremas con YOLOv8n + SAHI.
Inferencia por rebanadas (sliced prediction) para oclusión severa.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ultralytics import YOLO

try:
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    SAHI_AVAILABLE = True
except ImportError:
    SAHI_AVAILABLE = False

MODEL_NAME = "yolov8n.pt"
PERSON_CLASS = 0
CONFIDENCE = 0.25
IOU_THRESH = 0.7
SLICE_SIZE = 640
OVERLAP_RATIO = 0.2


def analyze_crowd(image_path: str) -> dict:
    """
    Procesa una imagen con SAHI (inferencia trozada) y retorna
    el conteo total de personas unificando todas las rebanadas.

    Args:
        image_path: Ruta absoluta o relativa a la imagen.

    Returns:
        dict con {"status": "success", "headcount": int}
        o {"status": "error", "message": str} en caso de fallo.
    """
    try:
        if not SAHI_AVAILABLE:
            return {
                "status": "error",
                "message": (
                    "SAHI no está instalado. Ejecutá: pip install sahi"
                ),
            }

        path = Path(image_path)
        if not path.is_file():
            return {"status": "error", "message": f"Archivo no encontrado: {image_path}"}

        detection_model = AutoDetectionModel.from_pretrained(
            model_type="ultralytics",
            model_path=MODEL_NAME,
            confidence_threshold=CONFIDENCE,
            device="cpu",
        )

        result = get_sliced_prediction(
            image=str(path),
            detection_model=detection_model,
            slice_height=SLICE_SIZE,
            slice_width=SLICE_SIZE,
            overlap_height_ratio=OVERLAP_RATIO,
            overlap_width_ratio=OVERLAP_RATIO,
            postprocess_type="NMS",
            postprocess_match_metric="IOS",
            postprocess_match_threshold=IOU_THRESH,
            verbose=False,
        )

        headcount = sum(
            1 for obj in result.object_prediction_list
            if obj.category.id == PERSON_CLASS
        )

        return {"status": "success", "headcount": headcount}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python crowd_counter_sahi.py <ruta_de_imagen>")
        return 1

    result = analyze_crowd(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
