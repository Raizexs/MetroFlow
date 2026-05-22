"""
Conteo direccional por línea virtual (entrada/salida tipo torniquete de metro).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

MIN_VISIBLE_FRAMES = 3


@dataclass(frozen=True)
class TrackPoint:
    track_id: int
    cx: float
    cy: float
    conf: float = 0.0


@dataclass(frozen=True)
class CrossingEvent:
    kind: Literal["entry", "exit"]
    track_id: int


def parse_line_coords(value: str) -> tuple[int, int, int, int]:
    """Parsea 'x1,y1,x2,y2' a coordenadas enteras."""
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"Línea inválida '{value}': se espera x1,y1,x2,y2")
    return tuple(int(p) for p in parts)  # type: ignore[return-value]


def side_of_line(px: float, py: float, x1: int, y1: int, x2: int, y2: int) -> float:
    """Signo del semiplano respecto a la línea (x1,y1)->(x2,y2). Positivo = un lado, negativo = otro."""
    return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)


def segments_intersect(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    cx: float,
    cy: float,
    dx: float,
    dy: float,
) -> bool:
    """True si el segmento AB intersecta el segmento CD."""

    def orient(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> float:
        return (qy - py) * (rx - qx) - (qx - px) * (ry - qy)

    o1 = orient(ax, ay, bx, by, cx, cy)
    o2 = orient(ax, ay, bx, by, dx, dy)
    o3 = orient(cx, cy, dx, dy, ax, ay)
    o4 = orient(cx, cy, dx, dy, bx, by)

    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    def on_segment(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> bool:
        return (
            min(px, rx) <= qx <= max(px, rx)
            and min(py, ry) <= qy <= max(py, ry)
        )

    if o1 == 0 and on_segment(ax, ay, cx, cy, bx, by):
        return True
    if o2 == 0 and on_segment(ax, ay, dx, dy, bx, by):
        return True
    if o3 == 0 and on_segment(cx, cy, ax, ay, dx, dy):
        return True
    if o4 == 0 and on_segment(cx, cy, bx, by, dx, dy):
        return True
    return False


def boundary_x_at_y(px: float, py: float, x1: int, y1: int, x2: int, y2: int) -> float:
    """Coordenada X del punto en la línea a la altura ``py`` (interpola/extrapola)."""
    del px  # API simétrica por si se usa en lambdas
    if abs(y2 - y1) < 1e-6:
        return float(x1)
    t = (py - y1) / (y2 - y1)
    return float(x1 + t * (x2 - x1))


class PerspectiveLineCounter:
    """
    Límite con perspectiva para andenes angulados y varias puertas.
    Por defecto el tren está a la derecha (mayor X = dentro del vagón).
    """

    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        *,
        train_on_right: bool = True,
        margin_px: float = 8.0,
        min_visible_frames: int = MIN_VISIBLE_FRAMES,
    ) -> None:
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.train_on_right = train_on_right
        self.margin_px = margin_px
        self.min_visible_frames = min_visible_frames
        self.inside_positive = train_on_right  # compatibilidad con annotate

        self.entries = 0
        self.exits = 0
        self._last_pos: dict[int, tuple[float, float]] = {}
        self._visible_frames: dict[int, int] = {}
        self._last_inside: dict[int, bool] = {}
        self._active_ids: set[int] = set()

    def _boundary_x(self, py: float) -> float:
        return boundary_x_at_y(0.0, py, self.x1, self.y1, self.x2, self.y2)

    def _is_inside(self, px: float, py: float) -> bool:
        bx = self._boundary_x(py)
        if self.train_on_right:
            return px > bx + self.margin_px
        return px < bx - self.margin_px

    @property
    def in_zone(self) -> int:
        count = 0
        for tid in self._active_ids:
            if self._visible_frames.get(tid, 0) < self.min_visible_frames:
                continue
            pos = self._last_pos.get(tid)
            if pos and self._is_inside(pos[0], pos[1]):
                count += 1
        return count

    def update(self, tracks: list[TrackPoint]) -> CrossingEvent | None:
        event: CrossingEvent | None = None
        current_ids = {t.track_id for t in tracks}

        for tp in tracks:
            tid = tp.track_id
            self._visible_frames[tid] = self._visible_frames.get(tid, 0) + 1
            prev = self._last_pos.get(tid)
            self._last_pos[tid] = (tp.cx, tp.cy)

            if self._visible_frames[tid] < self.min_visible_frames:
                self._last_inside[tid] = self._is_inside(tp.cx, tp.cy)
                continue

            curr_inside = self._is_inside(tp.cx, tp.cy)
            prev_inside = self._last_inside.get(tid)

            if prev is not None and prev_inside is not None and prev_inside != curr_inside:
                if curr_inside:
                    self.entries += 1
                    event = CrossingEvent(kind="entry", track_id=tid)
                else:
                    self.exits += 1
                    event = CrossingEvent(kind="exit", track_id=tid)

            self._last_inside[tid] = curr_inside

        self._active_ids = current_ids
        return event


def parse_lines_coords(value: str) -> list[tuple[int, int, int, int]]:
    """Varias líneas separadas por ``;`` (una por puerta)."""
    chunks = [c.strip() for c in value.split(";") if c.strip()]
    if not chunks:
        raise ValueError("Se esperaba al menos una línea x1,y1,x2,y2")
    return [parse_line_coords(chunk) for chunk in chunks]


class MultiLineCrossingCounter:
    """Varias líneas (puertas); agrega entradas/salidas y ``in_zone`` si está dentro en alguna."""

    def __init__(
        self,
        lines: list[tuple[int, int, int, int]],
        *,
        perspective: bool = False,
        train_on_right: bool = True,
        inside_positive: bool = True,
    ) -> None:
        self.counters: list[LineCrossingCounter | PerspectiveLineCounter] = []
        for x1, y1, x2, y2 in lines:
            if perspective:
                self.counters.append(
                    PerspectiveLineCounter(
                        x1, y1, x2, y2, train_on_right=train_on_right
                    )
                )
            else:
                self.counters.append(
                    LineCrossingCounter(x1, y1, x2, y2, inside_positive=inside_positive)
                )
        self.inside_positive = inside_positive

    @property
    def entries(self) -> int:
        return sum(c.entries for c in self.counters)

    @property
    def exits(self) -> int:
        return sum(c.exits for c in self.counters)

    @property
    def in_zone(self) -> int:
        inside_ids: set[int] = set()
        for counter in self.counters:
            for tid in counter._active_ids:
                if counter._visible_frames.get(tid, 0) < counter.min_visible_frames:
                    continue
                pos = counter._last_pos.get(tid)
                if pos and counter._is_inside(pos[0], pos[1]):
                    inside_ids.add(tid)
        return len(inside_ids)

    def update(self, tracks: list[TrackPoint]) -> CrossingEvent | None:
        event: CrossingEvent | None = None
        for counter in self.counters:
            ev = counter.update(tracks)
            if ev is not None:
                event = ev
        return event


def create_boundary_counter(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    *,
    perspective: bool = False,
    train_on_right: bool = True,
    inside_positive: bool = True,
    extra_lines: list[tuple[int, int, int, int]] | None = None,
) -> LineCrossingCounter | PerspectiveLineCounter | MultiLineCrossingCounter:
    lines = [(x1, y1, x2, y2)]
    if extra_lines:
        lines.extend(extra_lines)
    if len(lines) > 1:
        return MultiLineCrossingCounter(
            lines,
            perspective=perspective,
            train_on_right=train_on_right,
            inside_positive=inside_positive,
        )
    lx1, ly1, lx2, ly2 = lines[0]
    # Línea casi horizontal: mejor semiplano clásico (no perspectiva por Y)
    nearly_horizontal = abs(ly2 - ly1) <= max(12, int(abs(lx2 - lx1) * 0.08))
    if perspective and not nearly_horizontal:
        return PerspectiveLineCounter(
            lx1, ly1, lx2, ly2, train_on_right=train_on_right
        )
    return LineCrossingCounter(lx1, ly1, lx2, ly2, inside_positive=inside_positive)


class LineCrossingCounter:
    """
    Cuenta entradas/salidas cuando un track cruza la línea virtual.
    ``inside_positive=True`` significa que el semiplano con side > 0 es "dentro del metro".
    """

    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        *,
        inside_positive: bool = True,
        min_visible_frames: int = MIN_VISIBLE_FRAMES,
    ) -> None:
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.inside_positive = inside_positive
        self.min_visible_frames = min_visible_frames

        self.entries = 0
        self.exits = 0

        self._last_pos: dict[int, tuple[float, float]] = {}
        self._visible_frames: dict[int, int] = {}
        self._last_inside: dict[int, bool] = {}
        self._active_ids: set[int] = set()

    def _is_inside(self, px: float, py: float) -> bool:
        s = side_of_line(px, py, self.x1, self.y1, self.x2, self.y2)
        if s == 0:
            return False
        positive = s > 0
        return positive if self.inside_positive else not positive

    @property
    def in_zone(self) -> int:
        """Personas actualmente en el lado 'dentro' con tracking estable."""
        count = 0
        for tid in self._active_ids:
            if self._visible_frames.get(tid, 0) < self.min_visible_frames:
                continue
            pos = self._last_pos.get(tid)
            if pos and self._is_inside(pos[0], pos[1]):
                count += 1
        return count

    def reset_frame_ids(self, current_ids: set[int]) -> None:
        """Marca tracks no vistos en este frame (mantiene estado para re-apariciones)."""
        self._active_ids = current_ids

    def update(self, tracks: list[TrackPoint]) -> CrossingEvent | None:
        event: CrossingEvent | None = None
        current_ids = {t.track_id for t in tracks}

        for tp in tracks:
            tid = tp.track_id
            self._visible_frames[tid] = self._visible_frames.get(tid, 0) + 1

            prev = self._last_pos.get(tid)
            self._last_pos[tid] = (tp.cx, tp.cy)

            if self._visible_frames[tid] < self.min_visible_frames:
                self._last_inside[tid] = self._is_inside(tp.cx, tp.cy)
                continue

            curr_inside = self._is_inside(tp.cx, tp.cy)
            prev_inside = self._last_inside.get(tid)

            if prev is not None and prev_inside is not None:
                crossed = segments_intersect(
                    prev[0],
                    prev[1],
                    tp.cx,
                    tp.cy,
                    float(self.x1),
                    float(self.y1),
                    float(self.x2),
                    float(self.y2),
                )
                if crossed and prev_inside != curr_inside:
                    if curr_inside:
                        self.entries += 1
                        event = CrossingEvent(kind="entry", track_id=tid)
                    else:
                        self.exits += 1
                        event = CrossingEvent(kind="exit", track_id=tid)

            self._last_inside[tid] = curr_inside

        self._active_ids = current_ids
        return event
