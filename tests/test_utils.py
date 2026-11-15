import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (FpsEstimator, format_elapsed, mask_url, target_size,
                   timestamped_name, validate_url)


class TestValidateUrl(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_url("http://192.168.1.23:8080/video"), "http://192.168.1.23:8080/video")

    def test_bad_scheme(self):
        with self.assertRaises(ValueError):
            validate_url("htp://camera")

    def test_empty(self):
        with self.assertRaises(ValueError):
            validate_url("")

    def test_bad_port(self):
        with self.assertRaises(ValueError):
            validate_url("http://192.168.1.23:abc/video")

    def test_no_host(self):
        with self.assertRaises(ValueError):
            validate_url("http://")


class TestHelpers(unittest.TestCase):
    def test_resize_1920x1080_to_960(self):
        self.assertEqual(target_size(1920, 1080, 960), (960, 540))

    def test_resize_keeps_ratio_portrait(self):
        self.assertEqual(target_size(720, 1280, 360), (360, 640))

    def test_resize_invalid(self):
        with self.assertRaises(ValueError):
            target_size(0, 100, 50)

    def test_mask_url(self):
        self.assertNotIn("secret", mask_url("http://admin:secret@10.0.0.5:8080/video"))

    def test_names_unique_and_formatted(self):
        a = timestamped_name("screenshot", "jpg", datetime(2026, 11, 11, 8, 31, 5, 1000))
        b = timestamped_name("screenshot", "jpg", datetime(2026, 11, 11, 8, 31, 5, 2000))
        self.assertEqual(a, "screenshot_2026-11-11_08-31-05_001.jpg")
        self.assertNotEqual(a, b)

    def test_elapsed(self):
        self.assertEqual(format_elapsed(75), "01:15")


class TestFps(unittest.TestCase):
    def test_steady_30fps(self):
        est = FpsEstimator()
        for i in range(60):
            fps = est.tick(i / 30)
        self.assertAlmostEqual(fps, 30, delta=0.5)


if __name__ == "__main__":
    unittest.main()
