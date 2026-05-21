"""
Prueba YOLOv8n con tus propias fotos o videos.

Uso rápido:
    python detect_media.py --image ruta/a/mi_foto.jpg
    python detect_media.py --video ruta/a/mi_video.mp4
    python detect_media.py --dir ruta/carpeta_con_fotos
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import cv2

from config import CONF_THRESHOLD, MODEL_NAME, PERSON_CLASS_ID
from detector import PersonDetector

logger = logging.getLogger("detect_media")


def draw_boxes(
    frame: cv2.Mat,
    results,
    conf_threshold: float = CONF_THRESHOLD,
) -> tuple[cv2.Mat, int]:
    """Dibuja bounding boxes de personas detectadas y devuelve el conteo."""
    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return frame, 0

    count = 0
    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i].item())
        conf = boxes.conf[i].item()
        if cls_id != PERSON_CLASS_ID or conf < conf_threshold:
            continue
        count += 1
        x1, y1, x2, y2 = map(int, boxes.xyxy[i].tolist())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"persona {conf:.2f}"
        cv2.putText(
            frame, label, (x1, y1 - 6),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
        )

    return frame, count


def process_image(
    detector: PersonDetector,
    path: Path,
    output_dir: Path | None,
    show: bool,
) -> int:
    img = cv2.imread(str(path))
    if img is None:
        logger.error("No se pudo leer la imagen: %s", path)
        return 0

    results = detector._model(img, verbose=False)
    annotated, count = draw_boxes(img, results)

    print(f"  {path.name}: {count} personas detectadas")

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"{path.stem}_detectado{path.suffix}"
        cv2.imwrite(str(out_path), annotated)
        print(f"    → Guardado: {out_path}")

    if show:
        cv2.imshow(f"Detección — {path.name}", annotated)
        print("    Presiona cualquier tecla para continuar…")
        cv2.waitKey(0)
        cv2.destroyWindow(f"Detección — {path.name}")

    return count


def process_video(
    detector: PersonDetector,
    path: Path,
    output_dir: Path | None,
    show: bool,
    max_frames: int | None,
) -> list[int]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        logger.error("No se pudo abrir el video: %s", path)
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_video = cv2.VideoWriter(
            str(output_dir / f"{path.stem}_detectado.mp4"),
            fourcc, fps, (w, h),
        )

    counts: list[int] = []
    frame_idx = 0

    print(f"Video: {path.name} | {total_frames} frames | {fps:.1f} fps")

    while True:
        if max_frames is not None and frame_idx >= max_frames:
            break
        ok, frame = cap.read()
        if not ok:
            break

        results = detector._model(frame, verbose=False)
        annotated, count = draw_boxes(frame, results)
        counts.append(count)

        if output_dir:
            out_video.write(annotated)

        if show:
            cv2.imshow(f"Detección — {path.name}", annotated)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        frame_idx += 1
        if frame_idx % 30 == 0:
            print(f"  frame {frame_idx}/{total_frames} — personas: {count}")

    cap.release()
    if output_dir:
        out_video.release()
    if show:
        cv2.destroyAllWindows()

    return counts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prueba YOLOv8n con tus propias fotos/videos."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", type=Path, help="Ruta a una imagen")
    group.add_argument("--video", type=Path, help="Ruta a un video MP4")
    group.add_argument("--dir", type=Path, help="Carpeta con imágenes")
    parser.add_argument("--show", action="store_true", help="Mostrar ventana con detecciones")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Carpeta de salida")
    parser.add_argument("--max-frames", type=int, default=None, help="Límite de frames (video)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging DEBUG")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s | %(message)s",
    )

    logger.info("Cargando modelo %s...", MODEL_NAME)
    detector = PersonDetector()

    if args.image:
        if not args.image.is_file():
            logger.error("Archivo no encontrado: %s", args.image)
            return 1
        count = process_image(detector, args.image, args.output, args.show)
        print(f"\nTotal: {count} personas")

    elif args.video:
        if not args.video.is_file():
            logger.error("Archivo no encontrado: %s", args.video)
            return 1
        counts = process_video(detector, args.video, args.output, args.show, args.max_frames)
        if counts:
            print(f"\nResumen del video — frames procesados: {len(counts)}")
            print(f"  mínimo: {min(counts)} | máximo: {max(counts)} | promedio: {sum(counts)/len(counts):.1f}")

    elif args.dir:
        if not args.dir.is_dir():
            logger.error("Carpeta no encontrada: %s", args.dir)
            return 1
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        images = [p for p in sorted(args.dir.iterdir()) if p.suffix.lower() in exts]
        if not images:
            logger.error("No se encontraron imágenes en: %s", args.dir)
            return 1
        print(f"Procesando {len(images)} imágenes en {args.dir}...")
        total = 0
        for img_path in images:
            total += process_image(detector, img_path, args.output, args.show)
        print(f"\nTotal acumulado: {total} personas")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
