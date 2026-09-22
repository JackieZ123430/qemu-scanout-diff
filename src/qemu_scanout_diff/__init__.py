"""Raw QEMU framebuffer capture and regression analysis."""

from .core import FrameSpec, analyze_frame, compare_frames

__all__ = ["FrameSpec", "analyze_frame", "compare_frames"]
__version__ = "0.1.0"
