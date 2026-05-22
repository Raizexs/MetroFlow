"""Detector de personas con YOLO + ByteTrack (clase COCO 0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from config import CONF_THRESHOLD, MODEL_NAME, PERSON_CLASS_ID
from line_crossing import TrackPoint, side_of_line

if TYPE_CHECKING:
    from line_crossing import LineCrossingCounter


@dataclass
class AnnotateMeta:
    """Metadatos opcionales para overlay (línea de cruce, HUD)."""

    entries: int = 0
    exits: int = 0
    in_zone: int = 0
    flash_text: str | None = None
    line: tuple[int, int, int, int] | None = None


class PersonDetector:
    """Wrapper de inferencia sin efectos secundarios (sin I/O ni prints)."""

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        *,
        conf_threshold: float = CONF_THRESHOLD,
        imgsz: int = 1280,
    ) -> None:
        self._model = YOLO(model_name)
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz

    @staticmethod
    def count_persons(result: Results, conf_threshold: float = CONF_THRESHOLD) -> int:
        """Cuenta detecciones clase 0 (persona) con confianza > umbral."""
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return 0

        cls_mask = boxes.cls == PERSON_CLASS_ID
        conf_mask = boxes.conf > conf_threshold
        return int((cls_mask & conf_mask).sum().item())

    def detect(self, frame: np.ndarray) -> Results:
        """Inferencia sin tracking."""
        return self._model(
            frame,
            verbose=False,
            classes=[PERSON_CLASS_ID],
            conf=self.conf_threshold,
            imgsz=self.imgsz,
        )[0]

    def detect_and_track(self, frame: np.ndarray) -> Results:
        """Inferencia con ByteTrack y IDs persistentes."""
        results = self._model.track(
            frame,
            persist=True,
            verbose=False,
            classes=[PERSON_CLASS_ID],
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            tracker="bytetrack.yaml",
        )
        if not results:
            raise RuntimeError("track() no devolvió resultados")
        return results[0]

    def extract_tracks(self, result: Results) -> list[TrackPoint]:
        """Centroides e IDs desde un resultado con tracking."""
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return []

        tracks: list[TrackPoint] = []
        has_ids = boxes.id is not None

        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            conf = float(boxes.conf[i].item())
            if cls_id != PERSON_CLASS_ID or conf < self.conf_threshold:
                continue

            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0

            if has_ids:
                track_id = int(boxes.id[i].item())
            else:
                track_id = i

            tracks.append(TrackPoint(track_id=track_id, cx=cx, cy=cy, conf=conf))

        return tracks

    def count(self, frame: np.ndarray, *, track: bool = False) -> int:
        """Ejecuta inferencia en un fotograma y devuelve el conteo de personas."""
        if track:
            result = self.detect_and_track(frame)
            if result.boxes is None or result.boxes.id is None:
                return self.count_persons(result, self.conf_threshold)
            conf_mask = result.boxes.conf > self.conf_threshold
            return int(conf_mask.sum().item())

        result = self.detect(frame)
        return self.count_persons(result, self.conf_threshold)

    def annotate_frame(
        self,
        frame: np.ndarray,
        result: Results,
        *,
        counter: LineCrossingCounter | None = None,
        meta: AnnotateMeta | None = None,
    ) -> np.ndarray:
        """Dibuja cajas, IDs, línea virtual y HUD."""
        out = frame.copy()
        meta = meta or AnnotateMeta()

        if meta.line:
            x1, y1, x2, y2 = meta.line
            cv2.line(out, (x1, y1), (x2, y2), (0, 0, 255), 2, cv2.LINE_AA)
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            cv2.putText(
                out,
                "LINEA",
                (mid_x - 30, mid_y - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        boxes = result.boxes
        inside_positive = True
        if counter is not None:
            inside_positive = counter.inside_positive

        if boxes is not None:
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                if cls_id != PERSON_CLASS_ID or conf < self.conf_threshold:
                    continue

                x1, y1, x2, y2 = map(int, boxes.xyxy[i].tolist())
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2

                if counter is not None and meta.line:
                    if hasattr(counter, "_is_inside"):
                        inside = counter._is_inside(cx, cy)
                    else:
                        s = side_of_line(cx, cy, *meta.line)
                        positive = s > 0
                        inside = positive if inside_positive else not positive
                    color = (0, 200, 0) if inside else (0, 180, 255)
                else:
                    color = (0, 255, 0)

                cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
                tid = int(boxes.id[i].item()) if boxes.id is not None else i
                label = f"#{tid} {conf:.2f}"
                cv2.putText(
                    out,
                    label,
                    (x1, max(y1 - 6, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    color,
                    1,
                    cv2.LINE_AA,
                )

        hud_lines = [
            f"ENTRADAS: {meta.entries}  |  SALIDAS: {meta.exits}  |  EN ZONA: {meta.in_zone}",
        ]
        if meta.flash_text:
            hud_lines.append(meta.flash_text)

        y0 = 28
        for i, text in enumerate(hud_lines):
            color = (0, 255, 255) if i == 0 else (0, 220, 120)
            if i > 0 and meta.flash_text and text == meta.flash_text:
                color = (0, 255, 0)
            cv2.putText(
                out,
                text,
                (12, y0 + i * 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65 if i == 0 else 0.55,
                color,
                2,
                cv2.LINE_AA,
            )

        return out
