"""Envía un snapshot de ocupación al backend (Tarea 4)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from schemas import OccupationSnapshot


def push_snapshot(api_base: str, snapshot: OccupationSnapshot) -> dict:
    url = f"{api_base.rstrip('/')}/api/v1/analyze"
    body = json.dumps(snapshot.to_analyze_dict()).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="POST de telemetría IA al backend.")
    parser.add_argument(
        "--api",
        default="http://localhost:8000",
        help="URL base del backend",
    )
    parser.add_argument("--vagon-id", default="vagon_1")
    parser.add_argument("--headcount", type=int, required=True)
    parser.add_argument("--capacity", type=int, default=50)
    args = parser.parse_args()

    snapshot = OccupationSnapshot.from_detection(
        vagon_id=args.vagon_id,
        headcount=args.headcount,
        capacity=args.capacity,
    )

    try:
        result = push_snapshot(args.api, snapshot)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except urllib.error.URLError as exc:
        print(f"Error al conectar con el backend: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
