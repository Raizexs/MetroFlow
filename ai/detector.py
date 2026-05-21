"""Detector de personas con YOLOv8n (clase COCO 0)."""

from __future__ import annotations

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from config import CONF_THRESHOLD, MODEL_NAME, PERSON_CLASS_ID


class PersonDetector:
    """Wrapper de inferencia sin efectos secundarios (sin I/O ni prints)."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self._model = YOLO(model_name)

    @staticmethod
    def count_persons(result: Results) -> int:
        """Cuenta detecciones clase 0 (persona) con confianza > CONF_THRESHOLD."""
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return 0

        cls_mask = boxes.cls == PERSON_CLASS_ID
        conf_mask = boxes.conf > CONF_THRESHOLD
        return int((cls_mask & conf_mask).sum().item())

    def count(self, frame: np.ndarray, *, track: bool = False) -> int:
        """Ejecuta inferencia en un fotograma y devuelve el conteo de personas."""
        if track:
            results = self._model.track(frame, persist=True, verbose=False, classes=[PERSON_CLASS_ID])
            if not results or results[0].boxes is None:
                return 0
            boxes = results[0].boxes
            if boxes.id is None:
                return self.count_persons(results[0])
            conf_mask = boxes.conf > CONF_THRESHOLD
            return int((conf_mask).sum().item())

        result = self._model(frame, verbose=False)[0]
        return self.count_persons(result)
