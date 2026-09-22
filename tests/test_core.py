import tempfile
import unittest
from pathlib import Path
from qemu_scanout_diff.core import FrameSpec, analyze_bytes, compare_bytes, read_frame


class CoreTests(unittest.TestCase):
    def test_identical_frames(self):
        spec = FrameSpec(2, 2, 4)
        frame = bytes(spec.byte_size)
        result = compare_bytes(frame, frame, spec)
        self.assertTrue(result["same"])
        self.assertEqual(result["changed_bytes"], 0)
        self.assertIsNone(result["changed_bbox"])

    def test_changed_pixel_and_bbox(self):
        spec = FrameSpec(3, 2, 4)
        before = bytes(spec.byte_size)
        after = bytearray(before)
        offset = (1 * spec.width + 2) * spec.channels
        after[offset:offset + 4] = bytes((10, 20, 30, 255))
        result = compare_bytes(before, bytes(after), spec)
        self.assertEqual(result["changed_bytes"], 4)
        self.assertEqual(result["changed_pixels"], 1)
        self.assertEqual(result["changed_bbox"], {"min_x": 2, "min_y": 1, "max_x": 2, "max_y": 1})

    def test_nonblack_ignores_alpha_only_pixels(self):
        spec = FrameSpec(2, 1, 4)
        result = analyze_bytes(bytes((0, 0, 0, 255, 1, 0, 0, 0)), spec)
        self.assertEqual(result["nonblack_pixels"], 1)

    def test_size_validation(self):
        spec = FrameSpec(1, 1, 4)
        with tempfile.TemporaryDirectory() as directory:
            frame = Path(directory) / "short.rgba"
            frame.write_bytes(b"x")
            with self.assertRaises(ValueError):
                read_frame(frame, spec)


if __name__ == "__main__":
    unittest.main()
