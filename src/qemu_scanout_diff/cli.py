from __future__ import annotations

import argparse
import json
from pathlib import Path
from .core import FrameSpec, analyze_frame, compare_frames
from .hmp import capture_scanout
from .images import raw_to_png, write_diff_png


def _spec(args: argparse.Namespace) -> FrameSpec:
    return FrameSpec(args.width, args.height, args.channels)


def _add_frame_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--channels", type=int, choices=(3, 4), default=4)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qemu-scanout", description="Analyze and compare raw framebuffer scanouts.")
    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze one raw frame")
    analyze.add_argument("frame")
    _add_frame_args(analyze)
    analyze.add_argument("--png")
    compare = sub.add_parser("compare", help="Compare two raw frames")
    compare.add_argument("before")
    compare.add_argument("after")
    _add_frame_args(compare)
    compare.add_argument("--output-dir", type=Path)
    capture = sub.add_parser("capture", help="Run QEMU HMP pmemsave")
    capture.add_argument("output")
    capture.add_argument("--address", required=True, type=lambda value: int(value, 0))
    capture.add_argument("--size", type=int)
    capture.add_argument("--host", default="127.0.0.1")
    capture.add_argument("--port", type=int, default=4444)
    capture.add_argument("--timeout", type=float, default=3.0)
    _add_frame_args(capture)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        spec = _spec(args)
        result = analyze_frame(args.frame, spec)
        if args.png:
            raw_to_png(args.frame, args.png, spec)
            result["png"] = str(Path(args.png).resolve())
    elif args.command == "compare":
        spec = _spec(args)
        result = compare_frames(args.before, args.after, spec)
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            before_png = args.output_dir / "before.png"
            after_png = args.output_dir / "after.png"
            diff_png = args.output_dir / "diff.png"
            raw_to_png(args.before, before_png, spec)
            raw_to_png(args.after, after_png, spec)
            write_diff_png(args.before, args.after, diff_png, spec)
            result["images"] = {"before": str(before_png.resolve()), "after": str(after_png.resolve()), "diff": str(diff_png.resolve())}
            (args.output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        spec = _spec(args)
        size = args.size if args.size is not None else spec.byte_size
        response = capture_scanout(args.output, args.address, size, args.host, args.port, args.timeout)
        result = {"output": str(Path(args.output).resolve()), "address": f"0x{args.address:X}", "size": size, "monitor_response": response}
    print(json.dumps(result, indent=2))
    return 0
