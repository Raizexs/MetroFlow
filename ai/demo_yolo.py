"""
PoC premium: conteo de personas por fotograma con YOLOv8n.
Tarea 3 — aislado de FastAPI; contratos JSON alineados con Tareas 1 y 4.
"""

from __future__ import annotations

import argparse
import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

import cv2

from config import (
    AI_DIR,
    DEFAULT_CAPACITY,
    DEFAULT_SAMPLE_FPS,
    DEFAULT_VAGON_ID,
    DEFAULT_VIDEO,
    MODEL_NAME,
    PERSON_CLASS_ID,
    CONF_THRESHOLD,
)
from detector import PersonDetector
from schemas import OccupationSnapshot

logger = logging.getLogger("demo_yolo")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detecta personas en un video MP4 con YOLOv8n y emite conteos por frame."
    )
    parser.add_argument(
        "--video",
        type=Path,
        default=DEFAULT_VIDEO,
        help=f"Ruta al video MP4 (default: {DEFAULT_VIDEO})",
    )
    parser.add_argument(
        "--vagon-id",
        default=DEFAULT_VAGON_ID,
        help=f"Identificador de vagón/zona (default: {DEFAULT_VAGON_ID})",
    )
    parser.add_argument(
        "--capacity",
        type=int,
        default=DEFAULT_CAPACITY,
        help=f"Capacidad nominal del vagón para derivar status (default: {DEFAULT_CAPACITY})",
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=DEFAULT_SAMPLE_FPS,
        help=f"Fotogramas procesados por segundo (default: {DEFAULT_SAMPLE_FPS})",
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=None,
        help="Procesar 1 de cada N frames (anula --sample-fps si se define)",
    )
    parser.add_argument(
        "--format",
        choices=("console", "mock", "analyze"),
        default="console",
        dest="output_format",
        help="Formato de salida: consola, JSON mock (T1) o JSON analyze (T4)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Límite de frames leídos del video (demo rápida)",
    )
    parser.add_argument(
        "--push-api",
        default=None,
        help="URL base del backend; envía POST /api/v1/analyze por cada frame muestreado",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Logging DEBUG",
    )
    return parser.parse_args()


def push_to_api(api_base: str, snapshot: OccupationSnapshot) -> None:
    url = f"{api_base.rstrip('/')}/api/v1/analyze"
    body = json.dumps(snapshot.to_analyze_dict()).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        resp.read()


def resolve_stride(video_fps: float, sample_fps: float, explicit_stride: int | None) -> int:
    if explicit_stride is not None:
        return max(1, explicit_stride)
    if video_fps <= 0 or sample_fps <= 0:
        return 1
    return max(1, round(video_fps / sample_fps))


def emit_snapshot(snapshot: OccupationSnapshot, output_format: str) -> None:
    if output_format == "mock":
        print(json.dumps(snapshot.to_mock_dict(), ensure_ascii=False))
        return
    if output_format == "analyze":
        print(json.dumps(snapshot.to_analyze_dict(), ensure_ascii=False))
        return

    frame_label = snapshot.frame_index if snapshot.frame_index is not None else "?"
    print(f"Frame {frame_label}: {snapshot.headcount} personas detectadas")


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s | %(message)s",
    )

    video_path = args.video.resolve()
    if not video_path.is_file():
        logger.error("No se encontró el video en '%s'", video_path)
        logger.error(
            "Coloca un MP4 de ~10 s en %s o usa --video <ruta>.",
            AI_DIR / "videos" / "sample.mp4",
        )
        return 1

    if args.capacity < 1:
        logger.error("--capacity debe ser >= 1")
        return 1

    if args.sample_fps <= 0 and args.stride is None:
        logger.error("--sample-fps debe ser > 0")
        return 1

    logger.info("Cargando modelo %s...", MODEL_NAME)
    detector = PersonDetector()

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error("No se pudo abrir el video '%s'", video_path)
        return 1

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_s = total_frames / fps if fps > 0 else 0.0
    stride = resolve_stride(fps, args.sample_fps, args.stride)

    if args.output_format == "console":
        print(f"Video: {video_path.name}")
        print(f"Resolución: {width}x{height} | FPS: {fps:.2f} | Frames: {total_frames} | ~{duration_s:.1f}s")
        print(f"Vagón: {args.vagon_id} | Capacidad: {args.capacity}")
        print(f"Filtro: clase {PERSON_CLASS_ID} (person), confianza > {CONF_THRESHOLD}")
        print(f"Muestreo: stride={stride}" + (f" (~{fps / stride:.1f} fps efectivos)" if fps > 0 else ""))
        print("-" * 50)

    frame_index = 0
    processed = 0
    counts: list[int] = []

    while True:
        if args.max_frames is not None and frame_index >= args.max_frames:
            break

        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % stride == 0:
            headcount = detector.count(frame)
            counts.append(headcount)
            processed += 1

            snapshot = OccupationSnapshot.from_detection(
                vagon_id=args.vagon_id,
                headcount=headcount,
                capacity=args.capacity,
                frame_index=frame_index,
            )

            if args.push_api:
                try:
                    push_to_api(args.push_api, snapshot)
                    if args.output_format == "console":
                        print(
                            f"Frame {frame_index}: {headcount} personas → "
                            f"POST {args.push_api}/api/v1/analyze OK"
                        )
                except urllib.error.URLError as exc:
                    logger.error("POST fallido frame %s: %s", frame_index, exc)
            else:
                emit_snapshot(snapshot, args.output_format)

        frame_index += 1

    cap.release()

    if args.output_format == "console":
        print("-" * 50)
        print(f"Frames leídos: {frame_index} | Frames procesados: {processed}")
        if counts:
            print(
                f"Resumen — min: {min(counts)}, max: {max(counts)}, "
                f"promedio: {sum(counts) / len(counts):.1f}"
            )
        else:
            print("No se procesó ningún frame.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
