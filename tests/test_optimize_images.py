from pathlib import Path
import tempfile
import unittest
from PIL import Image
from scripts.optimize_images import optimize


class OptimizeImagesTests(unittest.TestCase):
    def test_outputs_expected_widths_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "incoming"
            output = root / "processed"
            source.mkdir()
            Image.new("RGB", (1600, 900), (30, 80, 150)).save(source / "hero.jpg")
            written, removed = optimize(source, output)
            self.assertEqual(written, 4)
            self.assertEqual(removed, 0)
            expected = ["hero-480w.webp", "hero-960w.webp", "hero-1440w.webp", "hero.webp"]
            self.assertEqual(sorted(p.name for p in output.glob("*.webp")), sorted(expected))
            self.assertEqual(optimize(source, output), (4, 0))
            with Image.open(output / "hero-960w.webp") as image:
                self.assertEqual(image.size, (960, 540))

    def test_preserves_transparency_and_does_not_upscale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "in"
            output = root / "out"
            source.mkdir()
            Image.new("RGBA", (320, 200), (10, 20, 30, 0)).save(source / "mark.png")
            written, _ = optimize(source, output)
            self.assertEqual(written, 1)
            with Image.open(output / "mark.webp") as image:
                self.assertEqual(image.size, (320, 200))
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.getpixel((0, 0))[3], 0)

    def test_deletes_stale_webp_derivatives(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "in"
            output = root / "out"
            source.mkdir()
            output.mkdir()
            Image.new("RGB", (700, 400), (80, 80, 80)).save(source / "current.png")
            Image.new("RGB", (20, 20), (0, 0, 0)).save(output / "removed.webp")
            written, removed = optimize(source, output)
            self.assertEqual(written, 2)
            self.assertEqual(removed, 1)
            self.assertFalse((output / "removed.webp").exists())

    def test_rejects_colliding_stems_without_partial_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "in"
            output = root / "out"
            source.mkdir()
            Image.new("RGB", (100, 100)).save(source / "photo.jpg")
            Image.new("RGB", (100, 100)).save(source / "photo.png")
            with self.assertRaisesRegex(ValueError, "same output name"):
                optimize(source, output)
            self.assertFalse(output.exists())

    def test_invalid_image_does_not_remove_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "in"
            output = root / "out"
            source.mkdir()
            output.mkdir()
            old = output / "existing.webp"
            Image.new("RGB", (30, 30), (1, 2, 3)).save(old)
            (source / "broken.jpg").write_bytes(b"not an image")
            with self.assertRaisesRegex(ValueError, "Cannot decode image"):
                optimize(source, output)
            self.assertTrue(old.exists())


if __name__ == "__main__":
    unittest.main()
