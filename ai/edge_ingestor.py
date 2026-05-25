"""
Edge ingestor: video + YOLO (--live) o guión de demo EFE (--preset efe por defecto).
POSTea telemetría al backend cada ~6 s, alineado con el dashboard.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import cv2

from config import (
    CONF_THRESHOLD,
    DEFAULT_EFE_LINE,
    DEFAULT_INFER_EVERY,
    DEFAULT_INSIDE_POSITIVE,
    DEFAULT_LINE,
    DEFAULT_PUSH_INTERVAL_SEC,
    DEFAULT_SAMPLE_FPS,
    DEFAULT_VAGON_ID,
    INFER_IMGSZ,
    MODEL_NAME,
)
from demo_timeline import EFE_DEMO_COOLDOWN_SEC, generate_random_dwell_schedule
from demo_yolo import push_to_api
from detector import PersonDetector
from line_crossing import create_boundary_counter, parse_line_coords, parse_lines_coords
from schemas import OccupationSnapshot
from video_presets import get_preset, resolve_default_video

logger = logging.getLogger("edge_ingestor")


def ingest_demo_timeline(
    *,
    api_base: str,
    zone_id: str,
    capacity: int,
    push_interval_sec: float,
    demo_seed: int | None = None,
) -> int:
    """Abordaje simulado: conteo aleatorio (sube/baja) durante detención 20–40 s."""
    schedule, dwell_sec, busy = generate_random_dwell_schedule(
        push_interval_sec,
        capacity=capacity,
        seed=demo_seed,
    )
    station_note = "estación de mayor flujo" if busy else "detención estándar"
    logger.info(
        "Modo demo EFE: %s POSTs cada %.0f s · ventana %.0f s (%s)",
        len(schedule),
        push_interval_sec,
        dwell_sec,
        station_note,
    )
    logger.info("Secuencia en zona: %s", [h for _, h in schedule])

    for t_sec, headcount in schedule:
        snapshot = OccupationSnapshot.from_detection(
            vagon_id=zone_id,
            headcount=headcount,
            capacity=capacity,
            frame_index=int(t_sec * 10),
        )
        push_to_api(api_base, snapshot)
        logger.info("Demo t=%.0fs: %s en zona → API", t_sec, headcount)
        if t_sec < schedule[-1][0]:
            time.sleep(push_interval_sec)

    logger.info(
        "Tren partió (fin ventana %.0f s). Sin más POST hasta próximo servicio (~%.0f min).",
        dwell_sec,
        EFE_DEMO_COOLDOWN_SEC / 60,
    )
    return 0


def ingest_video_live(
    *,
    source: Path,
    api_base: str,
    zone_id: str,
    capacity: int,
    max_frames: int | None,
    mode: str,
    line: tuple[int, int, int, int] | None,
    inside_positive: bool,
    perspective: bool,
    train_on_right: bool,
    extra_lines: list[tuple[int, int, int, int]] | None,
    push_interval_sec: float,
    infer_every: int,
    model_name: str,
    conf_threshold: float,
    imgsz: int,
) -> int:
    """YOLO + línea: inferencia frecuente (entradas/salidas) y POST al API cada ~push_interval."""
    detector = PersonDetector(
        model_name,
        conf_threshold=conf_threshold,
        imgsz=imgsz,
    )
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        logger.error("No se pudo abrir: %s", source)
        return 1

    counter = None
    if mode == "line":
        if line is None:
            logger.error("Modo line requiere --line x1,y1,x2,y2")
            return 1
        counter = create_boundary_counter(
            *line,
            perspective=perspective,
            train_on_right=train_on_right,
            inside_positive=inside_positive,
            extra_lines=extra_lines,
        )
        logger.info("Modo línea (%s): en_zona desde YOLO", "perspectiva" if perspective else "semiplano")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    infer_step = max(1, infer_every)
    api_stride = max(1, round(fps * push_interval_sec)) if push_interval_sec > 0 else 1
    frame_index = 0
    pushed = 0
    last_headcount = 0

    logger.info(
        "Video %.1f fps · infer cada %s frames · POST cada %s frames (~%.1f s) · modelo %s conf=%.2f",
        fps,
        infer_step,
        api_stride,
        api_stride / fps,
        model_name,
        conf_threshold,
    )

    while True:
        if max_frames is not None and frame_index >= max_frames:
            break
        ok, frame = cap.read()
        if not ok:
            break

        run_infer = frame_index % infer_step == 0
        if run_infer:
            if mode == "line" and counter is not None:
                result = detector.detect_and_track(frame)
                tracks = detector.extract_tracks(result)
                event = counter.update(tracks)
                last_headcount = counter.in_zone
                if event:
                    label = "ENTRADA" if event.kind == "entry" else "SALIDA"
                    logger.info(
                        "+%s (id #%s) | entradas=%s salidas=%s en_zona=%s",
                        label,
                        event.track_id,
                        counter.entries,
                        counter.exits,
                        counter.in_zone,
                    )
            else:
                last_headcount = detector.count(frame, track=True)

        if frame_index % api_stride == 0:
            if mode == "line" and counter is not None:
                headcount = counter.in_zone
            elif run_infer:
                headcount = last_headcount
            else:
                headcount = detector.count(frame, track=True)
            logger.info(
                "Frame %s → API headcount=%s%s",
                frame_index,
                headcount,
                (
                    f" (ent={counter.entries} sal={counter.exits})"
                    if counter is not None
                    else ""
                ),
            )
            snapshot = OccupationSnapshot.from_detection(
                vagon_id=zone_id,
                headcount=headcount,
                capacity=capacity,
                frame_index=frame_index,
            )
            push_to_api(api_base, snapshot)
            pushed += 1

            if push_interval_sec > 0:
                time.sleep(push_interval_sec)

        frame_index += 1

    cap.release()
    if counter is not None:
        logger.info(
            "Resumen línea: entradas=%s salidas=%s en_zona(final)=%s",
            counter.entries,
            counter.exits,
            counter.in_zone,
        )
    logger.info("Ingesta finalizada: %s frames leídos, %s POSTs", frame_index, pushed)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Edge ingestor → POST /api/v1/analyze")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--preset", choices=("efe", "metro_entrada", "sample"), default="efe")
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--zone-id", default=DEFAULT_VAGON_ID)
    parser.add_argument("--capacity", type=int, default=50)
    parser.add_argument("--sample-fps", type=float, default=None)
    parser.add_argument(
        "--push-interval",
        type=float,
        default=None,
        help="Segundos entre POST (default 6, igual que el dashboard).",
    )
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument(
        "--mode",
        choices=("count", "line"),
        default="line",
    )
    parser.add_argument("--line", default=None)
    parser.add_argument("--extra-lines", default=None)
    parser.add_argument("--perspective", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--train-on-right", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--infer-every", type=int, default=None)
    parser.add_argument("--model", default=None, help="Pesos YOLO (default preset o yolo11m.pt)")
    parser.add_argument("--conf", type=float, default=None, help="Umbral confianza (default preset o 0.4)")
    parser.add_argument("--imgsz", type=int, default=None, help="Tamaño inferencia (default 1280)")
    parser.add_argument(
        "--inside-positive",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_INSIDE_POSITIVE,
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Inferencia YOLO real sobre el video (sin guión demo).",
    )
    parser.add_argument(
        "--demo",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Demo EFE: ocupación aleatoria durante detención 20–40 s (default preset efe).",
    )
    parser.add_argument(
        "--demo-seed",
        type=int,
        default=None,
        help="Semilla opcional para repetir la misma secuencia aleatoria.",
    )
    args = parser.parse_args()

    preset = get_preset(args.preset)
    use_demo = args.demo
    if preset:
        if args.source is None:
            args.source = preset.video
        if args.line is None:
            args.line = preset.line
        if args.perspective is None:
            args.perspective = preset.perspective
        if args.train_on_right is None:
            args.train_on_right = preset.train_on_right
        if args.infer_every is None:
            args.infer_every = preset.infer_every
        if args.model is None:
            args.model = preset.model
        if args.conf is None:
            args.conf = preset.conf
        if args.imgsz is None:
            args.imgsz = preset.imgsz
        if args.extra_lines is None and preset.extra_lines:
            args.extra_lines = preset.extra_lines
        if args.sample_fps is None and preset.sample_fps is not None:
            args.sample_fps = preset.sample_fps
        if args.push_interval is None and preset.push_interval_sec is not None:
            args.push_interval = preset.push_interval_sec
        if use_demo is None and getattr(preset, "demo_timeline", False):
            use_demo = True

    if args.source is None:
        args.source = resolve_default_video()
    if args.line is None:
        args.line = DEFAULT_EFE_LINE
    if args.perspective is None:
        args.perspective = True
    if args.train_on_right is None:
        args.train_on_right = True
    if args.infer_every is None:
        args.infer_every = DEFAULT_INFER_EVERY
    if args.model is None:
        args.model = MODEL_NAME
    if args.conf is None:
        args.conf = CONF_THRESHOLD
    if args.imgsz is None:
        args.imgsz = INFER_IMGSZ
    if args.sample_fps is None:
        args.sample_fps = DEFAULT_SAMPLE_FPS
    if args.push_interval is None:
        args.push_interval = DEFAULT_PUSH_INTERVAL_SEC
    if use_demo is None:
        use_demo = not args.live

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    if use_demo and not args.live:
        logger.info("Preset %s: guión demo (use --live para YOLO sobre el video)", args.preset)
        return ingest_demo_timeline(
            api_base=args.api,
            zone_id=args.zone_id,
            capacity=args.capacity,
            push_interval_sec=max(0.0, args.push_interval),
            demo_seed=args.demo_seed,
        )

    if not args.source.is_file():
        logger.error("Fuente no encontrada: %s", args.source)
        return 1

    line_coords: tuple[int, int, int, int] | None = None
    extra: list[tuple[int, int, int, int]] = []
    if args.mode == "line":
        line_coords = parse_line_coords(args.line)
        if args.extra_lines:
            extra = parse_lines_coords(args.extra_lines)

    logger.info(
        "Modo live YOLO · infer cada %s frames · POST cada %.1f s",
        args.infer_every,
        args.push_interval,
    )
    return ingest_video_live(
        source=args.source.resolve(),
        api_base=args.api,
        zone_id=args.zone_id,
        capacity=args.capacity,
        max_frames=args.max_frames,
        mode=args.mode,
        line=line_coords,
        inside_positive=args.inside_positive,
        perspective=args.perspective,
        train_on_right=args.train_on_right,
        extra_lines=extra or None,
        push_interval_sec=max(0.0, args.push_interval),
        infer_every=args.infer_every,
        model_name=args.model,
        conf_threshold=args.conf,
        imgsz=args.imgsz,
    )


if __name__ == "__main__":
    raise SystemExit(main())
