"""
Demo MetroFlow: video con línea virtual, entradas/salidas y overlay en tiempo real.

Uso:
    python metro_demo_video.py --video videos/sample.mp4 --show
    python metro_demo_video.py --line 385,557,672,779 --output videos/metro_demo_salida.mp4
    python metro_demo_video.py --push-api http://localhost:8000 --show
"""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import cv2

from config import (
    AI_DIR,
    DEFAULT_CAPACITY,
    DEFAULT_DEMO_OUTPUT,
    DEFAULT_INFER_EVERY,
    DEFAULT_INFER_EVERY_SHOW,
    DEFAULT_INSIDE_POSITIVE,
    DEFAULT_LINE,
    DEFAULT_SAMPLE_FPS,
    DEFAULT_VAGON_ID,
    DEMO_CONF_THRESHOLD,
    DEMO_FAST_IMGSZ,
    DEMO_FAST_MODEL,
    DEFAULT_EFE_PLAYBACK_FPS,
    DEMO_PLAYBACK_FPS,
    INFER_IMGSZ,
    MODEL_NAME,
)
from demo_yolo import push_to_api, resolve_stride
from detector import AnnotateMeta, PersonDetector
from line_crossing import create_boundary_counter, parse_line_coords, parse_lines_coords
from schemas import OccupationSnapshot
from video_presets import get_preset, resolve_default_video

logger = logging.getLogger("metro_demo_video")

FLASH_FRAMES = 15


def resolve_video_path(path: Path | None) -> Path:
    if path is not None:
        return path.resolve()
    return resolve_default_video().resolve()


def apply_preset(args: argparse.Namespace) -> None:
    preset = get_preset(args.preset) if args.preset else None
    if preset is None:
        return
    args.video = preset.video
    args.line = preset.line
    args.perspective = preset.perspective
    args.train_on_right = preset.train_on_right
    args.inside_positive = preset.inside_positive
    args.infer_every = preset.infer_every
    args.conf = preset.conf
    if preset.extra_lines:
        args.extra_lines = preset.extra_lines
    if getattr(preset, "infer_every_show", None):
        args.infer_every_show = preset.infer_every_show
    if getattr(preset, "model", None):
        args.model = preset.model
    if getattr(preset, "imgsz", None):
        args.imgsz = preset.imgsz
    if getattr(preset, "playback_fps", None):
        args.playback_fps = preset.playback_fps


def read_playback_frame(
    cap: cv2.VideoCapture,
    *,
    source_fps: float,
    target_fps: float,
    pacing: dict[str, float],
) -> tuple[bool, np.ndarray | None]:
    """Muestrea el MP4 para reproducir a ``target_fps`` (p. ej. 60 desde 120)."""
    if target_fps <= 0 or source_fps <= 0 or target_fps >= source_fps:
        return cap.read()

    interval = source_fps / target_fps
    pacing.setdefault("accum", 0.0)

    while pacing["accum"] < interval:
        if not cap.grab():
            return False, None
        pacing["accum"] += 1.0

    pacing["accum"] -= interval
    return cap.read()


def apply_show_fast_defaults(args: argparse.Namespace, *, fps: float) -> None:
    """Acelera la ventana en vivo: menos frames, modelo n, sin MP4 por defecto."""
    preset = get_preset(args.preset)
    infer_show = (
        preset.infer_every_show
        if preset is not None
        else DEFAULT_INFER_EVERY_SHOW
    )
    args.model = DEMO_FAST_MODEL
    args.imgsz = DEMO_FAST_IMGSZ
    args.infer_every = max(args.infer_every, infer_show)
    if args.playback_fps is None:
        if args.preset == "efe":
            args.playback_fps = DEFAULT_EFE_PLAYBACK_FPS
        else:
            args.playback_fps = min(DEMO_PLAYBACK_FPS, fps) if fps > 0 else DEMO_PLAYBACK_FPS
    if not args.save:
        args.output = None


def default_line_for_frame(width: int, height: int) -> tuple[int, int, int, int]:
    """Línea horizontal al ~55% del alto si no se pasó --line."""
    y = int(height * 0.55)
    x1 = int(width * 0.15)
    x2 = int(width * 0.85)
    return x1, y, x2, y


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Demo video: detección + línea de cruce + HUD entradas/salidas."
    )
    parser.add_argument("--video", type=Path, default=None, help="MP4 de entrada")
    parser.add_argument(
        "--preset",
        choices=("efe", "metro_entrada", "sample"),
        default="efe",
        help="Calibración precargada (default: efe)",
    )
    parser.add_argument(
        "--line",
        default=None,
        help=f"Línea x1,y1,x2,y2 (default según preset o {DEFAULT_LINE})",
    )
    parser.add_argument(
        "--extra-lines",
        default=None,
        help="Puertas extra separadas por ';' (ej. dos umbrales más al fondo)",
    )
    parser.add_argument(
        "--perspective",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Modo perspectiva (tren a la derecha = mayor X). Auto en preset efe",
    )
    parser.add_argument(
        "--train-on-right",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Dentro del vagón = lado derecho del frame (EFE)",
    )
    parser.add_argument(
        "--inside-positive",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_INSIDE_POSITIVE,
        help="Solo modo línea clásica (semiplano side>0)",
    )
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument(
        "--save",
        action="store_true",
        help="Guardar MP4 (por defecto solo si no usas --show)",
    )
    parser.add_argument("--show", action="store_true", help="Ventana en vivo (modo rápido)")
    parser.add_argument(
        "--fast",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="yolo11n, imgsz 960, menos inferencias (auto con --show)",
    )
    parser.add_argument(
        "--playback-fps",
        type=float,
        default=None,
        help=f"FPS de ventana con --show (default {DEMO_PLAYBACK_FPS})",
    )
    parser.add_argument("--push-api", default=None, help="URL base API para POST analyze")
    parser.add_argument("--vagon-id", default=DEFAULT_VAGON_ID)
    parser.add_argument("--capacity", type=int, default=DEFAULT_CAPACITY)
    parser.add_argument("--model", default=MODEL_NAME)
    parser.add_argument("--conf", type=float, default=DEMO_CONF_THRESHOLD)
    parser.add_argument("--imgsz", type=int, default=INFER_IMGSZ)
    parser.add_argument(
        "--infer-every",
        type=int,
        default=None,
        help=f"Inferir 1 de cada N frames (default preset o {DEFAULT_INFER_EVERY})",
    )
    parser.add_argument(
        "--sample-fps",
        type=float,
        default=DEFAULT_SAMPLE_FPS,
        help="POST a API cada ~N fps efectivos",
    )
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--dense", action="store_true", help="SAHI en frames con conf media baja")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()


def try_dense_count(frame: np.ndarray) -> int | None:
    """Conteo SAHI opcional; devuelve headcount o None si no aplica."""
    try:
        from crowd_counter_sahi import analyze_crowd_frame
    except ImportError:
        return None

    result = analyze_crowd_frame(frame)
    if result.get("status") == "success":
        return int(result["headcount"])
    return None


def main() -> int:
    args = parse_args()
    apply_preset(args)
    if args.line is None:
        args.line = DEFAULT_LINE
    if args.perspective is None:
        args.perspective = args.preset == "efe"
    if args.train_on_right is None:
        args.train_on_right = True
    if args.infer_every is None:
        args.infer_every = DEFAULT_INFER_EVERY if args.preset == "efe" else 1

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s | %(message)s",
    )

    video_path = resolve_video_path(args.video)
    if not video_path.is_file():
        logger.error("Video no encontrado: %s", video_path)
        logger.error("Coloca un MP4 en %s o usa --video", AI_DIR / "videos")
        return 1

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error("No se pudo abrir: %s", video_path)
        return 1

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    use_fast = args.fast if args.fast is not None else args.show
    if use_fast:
        apply_show_fast_defaults(args, fps=fps)
    if args.playback_fps is None:
        args.playback_fps = DEMO_PLAYBACK_FPS if args.show else fps
    if args.output is None and (args.save or not args.show):
        args.output = DEFAULT_DEMO_OUTPUT

    try:
        lx1, ly1, lx2, ly2 = parse_line_coords(args.line)
    except ValueError:
        logger.warning("Línea inválida '%s'; usando auto según frame", args.line)
        lx1, ly1, lx2, ly2 = default_line_for_frame(width, height)

    extra: list[tuple[int, int, int, int]] = []
    if args.extra_lines:
        try:
            extra = parse_lines_coords(args.extra_lines)
        except ValueError as exc:
            logger.error("extra-lines inválido: %s", exc)
            return 1

    line_coords = (lx1, ly1, lx2, ly2)
    counter = create_boundary_counter(
        lx1, ly1, lx2, ly2,
        perspective=args.perspective,
        train_on_right=args.train_on_right,
        inside_positive=args.inside_positive,
        extra_lines=extra or None,
    )

    logger.info("Cargando modelo %s...", args.model)
    detector = PersonDetector(
        args.model,
        conf_threshold=args.conf,
        imgsz=args.imgsz,
    )

    writer: cv2.VideoWriter | None = None
    output_path: Path | None = None
    if args.output is not None:
        output_path = args.output.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    api_stride = resolve_stride(fps, args.sample_fps, None)
    infer_every = max(1, args.infer_every)
    pacing_state: dict[str, float] = {}
    use_playback_pacing = (
        args.show and fps > 0 and args.playback_fps > 0 and args.playback_fps < fps
    )

    flash_text: str | None = None
    flash_remaining = 0
    last_result = None
    frame_index = 0
    infer_count = 0
    t0 = time.perf_counter()

    mode = "perspectiva" if args.perspective else "semiplano"
    logger.info(
        "Video: %s (%dx%d, %.1f fps, %d frames) | Línea: %s | modo: %s | infer_every: %s | modelo: %s",
        video_path.name,
        width,
        height,
        fps,
        total_frames,
        line_coords,
        mode,
        infer_every,
        args.model,
    )
    if args.show:
        logger.info(
            "Ventana: %.0f fps (fuente %.0f) | imgsz %s | guardar MP4: %s",
            args.playback_fps,
            fps,
            args.imgsz,
            "sí" if writer else "no",
        )
    if extra:
        logger.info("Líneas extra (puertas): %s", extra)

    while True:
        if args.max_frames is not None and frame_index >= args.max_frames:
            break

        if use_playback_pacing:
            ok, frame = read_playback_frame(
                cap,
                source_fps=fps,
                target_fps=args.playback_fps,
                pacing=pacing_state,
            )
            if ok and frame is not None:
                frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        else:
            ok, frame = cap.read()

        if not ok or frame is None:
            break

        run_infer = frame_index % infer_every == 0

        if run_infer:
            last_result = detector.detect_and_track(frame)
            tracks = detector.extract_tracks(last_result)
            event = counter.update(tracks)

            if event:
                if event.kind == "entry":
                    flash_text = f"+1 ENTRADA (id #{event.track_id})"
                else:
                    flash_text = f"+1 SALIDA (id #{event.track_id})"
                flash_remaining = FLASH_FRAMES
                logger.info(
                    "%s | entradas=%s salidas=%s en_zona=%s",
                    flash_text,
                    counter.entries,
                    counter.exits,
                    counter.in_zone,
                )

            if args.dense and last_result.boxes is not None and len(last_result.boxes) > 0:
                mean_conf = float(last_result.boxes.conf.mean().item())
                if mean_conf < args.conf + 0.05:
                    dense_hc = try_dense_count(frame)
                    if dense_hc is not None and dense_hc > counter.in_zone:
                        logger.debug("SAHI refuerzo: %s personas", dense_hc)

            infer_count += 1

            if args.push_api and frame_index % api_stride == 0:
                snapshot = OccupationSnapshot.from_detection(
                    vagon_id=args.vagon_id,
                    headcount=counter.in_zone,
                    capacity=args.capacity,
                    frame_index=frame_index,
                )
                try:
                    push_to_api(args.push_api, snapshot)
                except Exception as exc:
                    logger.error("POST fallido: %s", exc)

        if flash_remaining > 0:
            flash_remaining -= 1
        elif flash_text:
            flash_text = None

        if last_result is not None:
            elapsed = time.perf_counter() - t0
            infer_fps = infer_count / elapsed if elapsed > 0 else 0.0
            meta = AnnotateMeta(
                entries=counter.entries,
                exits=counter.exits,
                in_zone=counter.in_zone,
                flash_text=flash_text,
                line=line_coords,
            )
            annotated = detector.annotate_frame(
                frame,
                last_result,
                counter=counter,
                meta=meta,
            )
            cv2.putText(
                annotated,
                f"FPS inferencia: {infer_fps:.1f}",
                (12, height - 16),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (180, 180, 180),
                1,
                cv2.LINE_AA,
            )
        else:
            annotated = frame

        if writer is not None:
            writer.write(annotated)

        if args.show:
            display = annotated
            if width > 1280:
                scale = 1280 / width
                display = cv2.resize(
                    annotated,
                    (1280, int(height * scale)),
                    interpolation=cv2.INTER_AREA,
                )
            cv2.imshow("MetroFlow — demo linea de cruce", display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break

        frame_index += 1

    cap.release()
    if writer is not None:
        writer.release()
    if args.show:
        cv2.destroyAllWindows()

    logger.info(
        "Listo: %s frames | entradas=%s salidas=%s",
        frame_index,
        counter.entries,
        counter.exits,
    )
    if output_path is not None:
        print(f"\nVideo guardado: {output_path}")
    print(f"ENTRADAS: {counter.entries} | SALIDAS: {counter.exits} | EN ZONA (final): {counter.in_zone}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
