"""
Edge ingestor (Tarea 4 / doc §4.A): lee video o carpeta de imágenes,
muestrea 1–5 fps, ejecuta YOLO local y POSTea telemetría al backend.
No persiste video; solo JSON anonimizado.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import cv2

from config import DEFAULT_SAMPLE_FPS, DEFAULT_VAGON_ID, DEFAULT_VIDEO
from demo_yolo import push_to_api, resolve_stride
from detector import PersonDetector
from schemas import OccupationSnapshot

logger = logging.getLogger("edge_ingestor")


def ingest_video(
    *,
    source: Path,
    api_base: str,
    zone_id: str,
    capacity: int,
    sample_fps: float,
    max_frames: int | None,
) -> int:
    detector = PersonDetector()
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        logger.error("No se pudo abrir: %s", source)
        return 1

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    stride = resolve_stride(fps, sample_fps, None)
    frame_index = 0
    pushed = 0

    while True:
        if max_frames is not None and frame_index >= max_frames:
            break
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % stride == 0:
            headcount = detector.count(frame)
            snapshot = OccupationSnapshot.from_detection(
                vagon_id=zone_id,
                headcount=headcount,
                capacity=capacity,
                frame_index=frame_index,
            )
            push_to_api(api_base, snapshot)
            pushed += 1
            logger.info("Frame %s: %s personas → API", frame_index, headcount)

        frame_index += 1

    cap.release()
    logger.info("Ingesta finalizada: %s frames, %s POSTs", frame_index, pushed)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Edge ingestor → POST /api/v1/analyze")
    parser.add_argument("--source", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--zone-id", default=DEFAULT_VAGON_ID)
    parser.add_argument("--capacity", type=int, default=50)
    parser.add_argument("--sample-fps", type=float, default=DEFAULT_SAMPLE_FPS)
    parser.add_argument("--max-frames", type=int, default=None)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    if not args.source.is_file():
        logger.error("Fuente no encontrada: %s", args.source)
        return 1

    return ingest_video(
        source=args.source.resolve(),
        api_base=args.api,
        zone_id=args.zone_id,
        capacity=args.capacity,
        sample_fps=args.sample_fps,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    raise SystemExit(main())
