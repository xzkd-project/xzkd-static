import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from tools.room_maps import build_room_maps

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_CODES = {
    "3A201",
    "3A202",
    "3A203",
    "3A204",
    "3A205",
    "3A206",
    "3A207",
    "3A208",
    "3A209",
    "3A210",
    "3A211",
    "3A212",
    "3A213",
    "3B201",
    "3B202",
}


class RoomMapBuildTest(unittest.TestCase):
    def test_publishes_all_annotated_pilot_rooms(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir)
            manifest_path = build_room_maps(ROOT / "static", output_dir)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            rooms = manifest["rooms"]
            self.assertEqual({room["code"] for room in rooms}, EXPECTED_CODES)
            self.assertEqual(len(rooms), len(EXPECTED_CODES))
            self.assertEqual(
                [room["code"] for room in rooms],
                sorted(EXPECTED_CODES),
            )

            source_path = ROOT / "static" / "imgs" / "三教主_02.png"
            with Image.open(source_path) as source:
                source_rgb = source.convert("RGB")
                for room in rooms:
                    self.assertEqual(room["building"], "三教主")
                    self.assertEqual(room["floor"], "2")
                    self.assertEqual(room["sourceImagePath"], "imgs/三教主_02.png")
                    image_path = output_dir / room["imagePath"]
                    self.assertTrue(image_path.is_file())
                    with Image.open(image_path) as rendered:
                        self.assertEqual(rendered.size, source.size)
                        self.assertIsNotNone(
                            ImageChops.difference(
                                source_rgb, rendered.convert("RGB")
                            ).getbbox()
                        )

    def test_render_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            first_dir = root / "first"
            second_dir = root / "second"
            build_room_maps(ROOT / "static", first_dir)
            build_room_maps(ROOT / "static", second_dir)

            first_manifest = (first_dir / "room_maps.json").read_bytes()
            second_manifest = (second_dir / "room_maps.json").read_bytes()
            self.assertEqual(first_manifest, second_manifest)
            for code in EXPECTED_CODES:
                first_image = (
                    first_dir / "imgs" / "rooms" / f"{code}.png"
                ).read_bytes()
                second_image = (
                    second_dir / "imgs" / "rooms" / f"{code}.png"
                ).read_bytes()
                self.assertEqual(
                    hashlib.sha256(first_image).digest(),
                    hashlib.sha256(second_image).digest(),
                )


if __name__ == "__main__":
    unittest.main()
