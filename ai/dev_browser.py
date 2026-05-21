"""
Navegador interactivo de fotos para probar YOLOv8n.
Usa flechitas ↑↓ para cambiar de foto, 'a' para analizar, ESC para salir.
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

import cv2
import msvcrt

from config import CONF_THRESHOLD, MODEL_NAME, PERSON_CLASS_ID
from detector import PersonDetector

SHOW_W = 1280
SHOW_H = 800


def clear_console() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def get_image_files(directory: Path) -> list[Path]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
    return sorted(
        p for p in directory.iterdir()
        if p.suffix.lower() in exts and p.is_file()
    )


def resize_for_display(img: cv2.Mat, max_w: int = SHOW_W, max_h: int = SHOW_H) -> cv2.Mat:
    h, w = img.shape[:2]
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return img


def draw_detections(frame: cv2.Mat, results, conf_threshold: float) -> tuple[cv2.Mat, int]:
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

    label_total = f"Total: {count} personas"
    cv2.putText(
        frame, label_total, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
    )
    return frame, count


MODEL_FAMILIES = {
    "v8": {"prefix": "yolov8", "sizes": ["n", "s", "m", "l", "x"]},
    "v11": {"prefix": "yolo11", "sizes": ["n", "s", "m", "l", "x"]},
}
MODEL_KEYS = list(MODEL_FAMILIES.keys())
DEFAULT_FAMILY = "v11"
DEFAULT_SIZE_IDX = 2  # m (yolo11m — mejor equilibrio precisión/velocidad para multitudes)


def current_model(family: str, size_idx: int) -> str:
    info = MODEL_FAMILIES[family]
    return f"{info['prefix']}{info['sizes'][size_idx]}.pt"


def model_label(model_name: str) -> str:
    for info in MODEL_FAMILIES.values():
        prefix = info["prefix"]
        if model_name.startswith(prefix):
            size = model_name.replace(prefix, "").replace(".pt", "")
            return f"{prefix.upper()}{size}"
    return model_name.replace(".pt", "")


def render_list(images: list[Path], selected: int, info: str, threshold: float, model_name: str) -> None:
    clear_console()
    print("=" * 60)
    print(f"  DEV BROWSER — {model_label(model_name)}")
    print("=" * 60)
    print(f"  Directorio: {images[0].parent}")
    print(f"  Total fotos: {len(images)}")
    print(f"  Confianza: \033[33m{threshold:.2f}\033[0m  ([/] para ajustar)")
    print(f"  Modelo:    \033[36m{model_label(model_name)}\033[0m  ([m] talla  |  [y] familia)")
    print("-" * 60)

    for i, img in enumerate(images):
        marker = " →" if i == selected else "  "
        line = f"  [{i + 1:3d}] {marker} {img.name}"
        if len(line) > 58:
            line = line[:55] + "..."
        if i == selected:
            print(f"\033[7m{line}\033[0m")
        else:
            print(line)

    print("-" * 60)

    if selected < len(images):
        path = images[selected]
        size = path.stat().st_size
        print(f"  Seleccionada: {path.name}  ({size // 1024} KB)")

    print("-" * 60)
    print(f"  {info}")
    print("-" * 60)
    print("  [↑/↓] Navegar  |  [z] Analizar + ventana  |  [x] Solo ventana")
    print("  [a] Bajar confianza  |  [d] Subir confianza  (step 0.05)")
    print("  [m] Talla n/s/m/l/x  |  [y] Familia YOLOv8/YOLO11  |  [r] Reset confianza")
    print("=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Navegador interactivo de fotos para probar YOLO."
    )
    parser.add_argument(
        "--dir", "-d",
        type=Path,
        default=Path.cwd(),
        help="Carpeta con imágenes (default: directorio actual)",
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=CONF_THRESHOLD,
        help=f"Umbral de confianza (default: {CONF_THRESHOLD})",
    )
    args = parser.parse_args()

    if not args.dir.is_dir():
        print(f"Error: '{args.dir}' no es una carpeta válida")
        return 1

    images = get_image_files(args.dir)
    if not images:
        print(f"No se encontraron imágenes en: {args.dir}")
        return 1

    family = DEFAULT_FAMILY
    size_idx = DEFAULT_SIZE_IDX
    model_name = current_model(family, size_idx)
    sys.stdout.write(f"Cargando {model_label(model_name)}...\n")
    sys.stdout.flush()
    detector = PersonDetector(model_name)
    clear_console()

    selected = 0
    threshold = args.threshold
    info = "Listo. Usa las flechas y presiona 'a' para analizar."

    while True:
        render_list(images, selected, info, threshold, model_name)

        key = msvcrt.getch()

        if key in (b"\xe0", b"\x00"):
            key = msvcrt.getch()
            if key == b"H":
                selected = (selected - 1) % len(images)
                info = ""
            elif key == b"P":
                selected = (selected + 1) % len(images)
                info = ""
            continue

        if key in (b"q", b"Q", b"\x1b"):
            clear_console()
            print("Saliste del navegador.")
            break

        if key in (b"d", b"D"):
            threshold = min(1.0, threshold + 0.05)
            info = f"Confianza subida a {threshold:.2f}"
            continue

        if key in (b"a", b"A"):
            threshold = max(0.05, threshold - 0.05)
            info = f"Confianza bajada a {threshold:.2f}"
            continue

        if key in (b"r", b"R"):
            threshold = 0.50
            info = "Confianza reiniciada a 0.50"
            continue

        if key in (b"m", b"M"):
            sizes = MODEL_FAMILIES[family]["sizes"]
            size_idx = (size_idx + 1) % len(sizes)
            model_name = current_model(family, size_idx)
            info = f"Cambiando a {model_label(model_name)}..."
            render_list(images, selected, info, threshold, model_name)
            detector = PersonDetector(model_name)
            info = f"Talla cambiada a {model_label(model_name)}"
            continue

        if key in (b"y", b"Y"):
            idx = MODEL_KEYS.index(family)
            family = MODEL_KEYS[(idx + 1) % len(MODEL_KEYS)]
            size_idx = min(size_idx, len(MODEL_FAMILIES[family]["sizes"]) - 1)
            model_name = current_model(family, size_idx)
            info = f"Cambiando a {model_label(model_name)}..."
            render_list(images, selected, info, threshold, model_name)
            detector = PersonDetector(model_name)
            info = f"Familia cambiada a {model_label(model_name)}"
            continue

        if key in (b"z", b"Z"):
            path = images[selected]
            info = f"Analizando {path.name} (confianza ≥ {threshold:.2f})..."

            img = cv2.imread(str(path))
            if img is None:
                info = f"Error: no se pudo leer {path.name}"
                continue

            results = detector._model(img, verbose=False)
            annotated, count = draw_detections(img, results, threshold)
            display = resize_for_display(annotated)

            out_dir = args.dir / "_detectado"
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / f"{path.stem}_detectado{path.suffix}"
            cv2.imwrite(str(out_path), annotated)

            title = f"{model_label(model_name)} — conf ≥ {threshold:.2f} — {path.name} — {count} personas"
            cv2.imshow(title, display)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            info = (
                f"✓ {path.name}: {count} personas (confianza ≥ {threshold:.2f}) "
                f"→ {out_path.name}"
            )
            continue

        if key in (b"x", b"X"):
            path = images[selected]
            img = cv2.imread(str(path))
            if img is None:
                info = f"Error: no se pudo leer {path.name}"
                continue

            results = detector._model(img, verbose=False)
            annotated, count = draw_detections(img, results, threshold)
            display = resize_for_display(annotated)

            title = f"{model_label(model_name)} — conf ≥ {threshold:.2f} — {path.name} — {count} personas"
            cv2.imshow(title, display)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            info = f"Ventana cerrada. {path.name}: {count} personas (confianza ≥ {threshold:.2f})"
            continue

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
