"""
Analiza un MP4 de demo: metadatos, personas por tramo y sugerencia de línea.

Uso:
    python analyze_video.py videos/efe-subway-arriving.mp4
    python analyze_video.py --preset efe
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from config import VIDEOS_DIR
from detector import PersonDetector
from line_crossing import PerspectiveLineCounter, create_boundary_counter, parse_line_coords
from video_presets import PRESETS, get_preset


def analyze(
    video_path: Path,
    *,
    line: str | None = None,
    perspective: bool = False,
    train_on_right: bool = True,
    infer_every: int = 8,
    max_frames: int | None = None,
) -> dict:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(video_path)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if line:
        x1, y1, x2, y2 = parse_line_coords(line)
    else:
        y = int(h * 0.62)
        x1, y1, x2, y2 = int(w * 0.12), y, int(w * 0.88), int(h * 0.38)

    counter = create_boundary_counter(
        x1, y1, x2, y2,
        perspective=perspective,
        train_on_right=train_on_right,
    )
    detector = PersonDetector(conf_threshold=0.35, imgsz=1280)

    fi = 0
    person_frames = 0
    max_persons = 0
    cx_values: list[float] = []

    while True:
        if max_frames is not None and fi >= max_frames:
            break
        ok, frame = cap.read()
        if not ok:
            break
        if fi % infer_every == 0:
            result = detector.detect(frame)
            n = 0
            if result.boxes is not None:
                n = len(result.boxes)
                for i in range(n):
                    x1b, y1b, x2b, y2b = result.boxes.xyxy[i].tolist()
                    cx_values.append((x1b + x2b) / 2.0)
            if n > 0:
                person_frames += 1
                max_persons = max(max_persons, n)
            if perspective and isinstance(counter, PerspectiveLineCounter):
                tracks = detector.extract_tracks(detector.detect_and_track(frame))
                counter.update(tracks)
        fi += 1

    cap.release()

    cx_values.sort()
    p50 = cx_values[len(cx_values) // 2] if cx_values else 0
    p90 = cx_values[int(len(cx_values) * 0.9)] if cx_values else 0

    return {
        "file": video_path.name,
        "resolution": f"{w}x{h}",
        "fps": round(fps, 2),
        "frames": total,
        "duration_s": round(total / fps, 2) if fps else 0,
        "suggested_line": f"{x1},{y1},{x2},{y2}",
        "perspective": perspective,
        "train_on_right": train_on_right,
        "frames_with_people": person_frames,
        "max_persons_in_frame": max_persons,
        "centroid_x_p50": round(p50, 1),
        "centroid_x_p90": round(p90, 1),
        "entries": getattr(counter, "entries", 0),
        "exits": getattr(counter, "exits", 0),
        "recommended_infer_every": max(1, int(round(fps / 30))) if fps > 35 else 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analiza video de demo MetroFlow")
    parser.add_argument("video", type=Path, nargs="?", default=None)
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.preset:
        preset = get_preset(args.preset)
        if preset is None:
            return 1
        path = preset.video
        report = analyze(
            path,
            line=preset.line,
            perspective=preset.perspective,
            train_on_right=preset.train_on_right,
            infer_every=preset.infer_every * 2,
        )
        report["preset"] = preset.name
        report["notes"] = preset.notes
        report["extra_lines"] = preset.extra_lines
    else:
        path = args.video or (VIDEOS_DIR / "efe-subway-arriving.mp4")
        report = analyze(path.resolve(), perspective=True, train_on_right=True)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Archivo: {report['file']}")
        print(f"Resolución: {report['resolution']} | {report['fps']} fps | {report['duration_s']} s")
        print(f"Personas: hasta {report['max_persons_in_frame']} por frame")
        print(f"Centroide X (p50/p90): {report['centroid_x_p50']} / {report['centroid_x_p90']}")
        print(f"Línea sugerida: {report['suggested_line']}")
        print(f"Modo perspectiva: {report['perspective']} | infer_every recomendado: {report['recommended_infer_every']}")
        if report.get("preset"):
            print(f"Preset: {report['preset']} — {report.get('notes', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
