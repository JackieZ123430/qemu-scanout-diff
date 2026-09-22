from __future__ import annotations

from pathlib import Path
from PIL import Image
from .core import FrameSpec, read_frame


def raw_to_png(raw_path: str | Path, png_path: str | Path, spec: FrameSpec) -> None:
    data = read_frame(raw_path, spec)
    Image.frombytes(spec.mode, (spec.width, spec.height), data).save(png_path)


def write_diff_png(before_path: str | Path, after_path: str | Path, output_path: str | Path, spec: FrameSpec) -> None:
    before = read_frame(before_path, spec)
    after = read_frame(after_path, spec)
    output = bytearray(spec.width * spec.height * 4)
    for pixel in range(spec.width * spec.height):
        source = pixel * spec.channels
        target = pixel * 4
        changed = any(before[source + c] != after[source + c] for c in range(spec.channels))
        if changed:
            output[target:target + 4] = bytes((255, 0, 255, 255))
        else:
            value = (before[source] + before[source + 1] + before[source + 2]) // 3
            dim = value // 4
            output[target:target + 4] = bytes((dim, dim, dim, 255))
    Image.frombytes("RGBA", (spec.width, spec.height), bytes(output)).save(output_path)
