"""
Calibra la línea virtual haciendo clic en dos puntos del primer frame del video.

Uso:
    python calibrate_line.py --video videos/sample.mp4
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from config import DEFAULT_EFE_VIDEO
from video_presets import resolve_default_video
from line_crossing import parse_line_coords


def main() -> int:
    parser = argparse.ArgumentParser(description="Calibrar línea x1,y1,x2,y2 con 2 clics")
    parser.add_argument(
        "--video",
        type=Path,
        default=None,
        help=f"MP4 (default: {DEFAULT_EFE_VIDEO.name} si existe)",
    )
    args = parser.parse_args()

    video = args.video or resolve_default_video()
    if not video.is_file():
        print(f"Video no encontrado: {video}")
        return 1

    cap = cv2.VideoCapture(str(video))
    ok, frame = cap.read()
    cap.release()
    if not ok:
        print("No se pudo leer el primer frame")
        return 1

    points: list[tuple[int, int]] = []
    window = "Calibrar linea — clic 1 y 2, ESC salir"

    def on_click(event: int, x: int, y: int, _flags: int, _param: object) -> None:
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            points.append((x, y))
            cv2.circle(display, (x, y), 6, (0, 255, 255), -1)
            if len(points) == 2:
                cv2.line(display, points[0], points[1], (0, 0, 255), 2)
            cv2.imshow(window, display)

    display = frame.copy()
    cv2.namedWindow(window)
    cv2.setMouseCallback(window, on_click)
    cv2.imshow(window, display)
    print("Haz clic en el inicio y fin de la línea (torniquete/puerta).")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(points) != 2:
        print("Se necesitan exactamente 2 puntos.")
        return 1

    line_str = f"{points[0][0]},{points[0][1]},{points[1][0]},{points[1][1]}"
    print(f"\nVideo: {video.name}")
    print(f"--line {line_str}")
    print("--perspective --train-on-right   # recomendado para EFE (tren a la derecha)")
    parse_line_coords(line_str)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
