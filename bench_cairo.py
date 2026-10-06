#!/usr/bin/env python3
"""Benchmark Cairo command replay, with librsvg processing outside timing.

Record the SVG once, then clear and replay onto one image surface per frame.
The recording stores drawing operations, including fills and strokes.
"""

import math
import sys
import time

import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg
import cairo

DEFAULT_ITERATIONS = 1000


def bench(filename: str, iterations: int = DEFAULT_ITERATIONS, scale: float = 1.0) -> None:
    handle = Rsvg.Handle.new_from_file(filename)
    ok, base_width, base_height = handle.get_intrinsic_size_in_pixels()
    if not ok:
        # no intrinsic pixel size (e.g. viewBox-only SVG); fall back to a default viewport
        base_width, base_height = 900, 900
    width = math.ceil(base_width * scale)
    height = math.ceil(base_height * scale)
    viewport = Rsvg.Rectangle()
    viewport.x = 0
    viewport.y = 0
    viewport.width = width
    viewport.height = height

    # Prepare the draw commands before timing, like Swift's svgDrawList.
    # render_document already scales to the viewport; do not also scale the context.
    recording = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, (0, 0, width, height))
    recording_ctx = cairo.Context(recording)
    handle.render_document(recording_ctx, viewport)

    # surface and context live across frames, matching the Swift bench which reuses one
    # canvas; each frame is clear + render, like a real frame loop
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_surface(recording, 0, 0)

    durations = []
    for _ in range(iterations):
        start = time.perf_counter()

        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.paint()

        durations.append(time.perf_counter() - start)

    total = sum(durations)
    average = total / iterations
    minimum = min(durations)
    maximum = max(durations)

    print(
        f"bench {filename} x{iterations} (Cairo recording replay): "
        f"total={total:.8f}s, avg={average * 1000:.6f}ms, "
        f"min={minimum * 1000:.6f}ms, max={maximum * 1000:.6f}ms"
    )


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "tiger.svg"
    bench(path)
