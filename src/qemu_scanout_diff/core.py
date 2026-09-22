from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FrameSpec:
    width: int
    height: int
    channels: int = 4

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.channels not in (3, 4):
            raise ValueError("channels must be 3 (RGB) or 4 (RGBA)")

    @property
    def byte_size(self) -> int:
        return self.width * self.height * self.channels

    @property
    def mode(self) -> str:
        return "RGBA" if self.channels == 4 else "RGB"


def read_frame(path: str | Path, spec: FrameSpec) -> bytes:
    data = Path(path).read_bytes()
    if len(data) != spec.byte_size:
        raise ValueError(
            f"frame size mismatch for {path}: expected {spec.byte_size} bytes, "
            f"got {len(data)}"
        )
    return data


def _nonblack_pixels(data: bytes, spec: FrameSpec) -> int:
    count = 0
    for offset in range(0, len(data), spec.channels):
        if data[offset] or data[offset + 1] or data[offset + 2]:
            count += 1
    return count


def analyze_bytes(data: bytes, spec: FrameSpec) -> dict[str, Any]:
    if len(data) != spec.byte_size:
        raise ValueError(
            f"frame size mismatch: expected {spec.byte_size} bytes, got {len(data)}"
        )
    return {
        "spec": asdict(spec),
        "byte_size": len(data),
        "sha256": sha256(data).hexdigest().upper(),
        "nonblack_pixels": _nonblack_pixels(data, spec),
    }


def analyze_frame(path: str | Path, spec: FrameSpec) -> dict[str, Any]:
    result = analyze_bytes(read_frame(path, spec), spec)
    result["path"] = str(Path(path).resolve())
    return result


def compare_bytes(before: bytes, after: bytes, spec: FrameSpec) -> dict[str, Any]:
    if len(before) != spec.byte_size or len(after) != spec.byte_size:
        raise ValueError("both frames must match the configured frame size")

    changed_bytes = 0
    changed_pixels = 0
    min_x, min_y = spec.width, spec.height
    max_x = max_y = -1

    for offset in range(0, spec.byte_size, spec.channels):
        pixel_changed = False
        for channel in range(spec.channels):
            if before[offset + channel] != after[offset + channel]:
                changed_bytes += 1
                pixel_changed = True
        if pixel_changed:
            changed_pixels += 1
            pixel = offset // spec.channels
            x = pixel % spec.width
            y = pixel // spec.width
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    bbox = None
    if changed_pixels:
        bbox = {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}

    return {
        "spec": asdict(spec),
        "same": changed_bytes == 0,
        "changed_bytes": changed_bytes,
        "changed_pixels": changed_pixels,
        "changed_bbox": bbox,
        "before": analyze_bytes(before, spec),
        "after": analyze_bytes(after, spec),
    }


def compare_frames(before_path: str | Path, after_path: str | Path, spec: FrameSpec) -> dict[str, Any]:
    result = compare_bytes(read_frame(before_path, spec), read_frame(after_path, spec), spec)
    result["before"]["path"] = str(Path(before_path).resolve())
    result["after"]["path"] = str(Path(after_path).resolve())
    return result
