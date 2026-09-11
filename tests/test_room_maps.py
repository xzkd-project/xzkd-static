import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from tools.room_maps import RoomMapError, build_room_maps

ROOT = Path(__file__).resolve().parent.parent
PILOT_CODES = {
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
    def test_publishes_annotated_rooms_across_buildings(self) -> None:
        annotations = json.loads(
            (ROOT / "static" / "room_map_annotations.json").read_text(encoding="utf-8")
        )
        expected = {
            room["code"]: floor
            for floor in annotations["maps"]
            for room in floor["rooms"]
        }
        rules = json.loads((ROOT / "static/building_img_rules.json").read_text())
        self.assertEqual(
            {floor["sourceImagePath"] for floor in annotations["maps"]},
            {rule["path"].removeprefix("./") for rule in rules},
        )
        for code, floor in expected.items():
            matched = next(rule for rule in rules if re.fullmatch(rule["regex"], code))
            self.assertEqual(
                floor["sourceImagePath"], matched["path"].removeprefix("./")
            )
        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir)
            manifest_path = build_room_maps(ROOT / "static", output_dir)
            rooms = json.loads(manifest_path.read_text(encoding="utf-8"))["rooms"]
            codes = {room["code"] for room in rooms}
            self.assertEqual(codes, set(expected))
            self.assertEqual(len(rooms), len(expected))
            self.assertTrue(codes >= PILOT_CODES)
            self.assertTrue(
                {
                    "5201",
                    "1101",
                    "2103",
                    "GT-A401",
                    "G2-B302",
                    "GH-104",
                    "ARTS401",
                    "GX-C1001",
                    "Z101",
                }
                <= codes
            )
            self.assertEqual([room["code"] for room in rooms], sorted(codes))
            for room in rooms:
                floor = expected[room["code"]]
                self.assertEqual(room["building"], floor["building"])
                self.assertEqual(room["floor"], floor["floor"])
                self.assertEqual(room["sourceImagePath"], floor["sourceImagePath"])
                with (
                    Image.open(ROOT / "static" / room["sourceImagePath"]) as source,
                    Image.open(output_dir / room["imagePath"]) as rendered,
                ):
                    self.assertEqual(rendered.size, source.size)
                    self.assertIsNotNone(
                        ImageChops.difference(
                            source.convert("RGB"), rendered.convert("RGB")
                        ).getbbox()
                    )
            # Pin room locations that previously lacked coverage or were easy to
            # confuse with a neighboring room or the unnumbered teacher lounge.
            for code, target, neighbor in [
                ("5201", (1700, 640), (1400, 640)),
                ("3A105", (1640, 600), (1570, 670)),
                ("3A106", (1790, 500), (1640, 600)),
                ("3A107", (1770, 340), (1790, 500)),
                ("3A308", (1430, 540), (1060, 540)),
                ("3A310", (1060, 540), (1430, 540)),
            ]:
                with (
                    self.subTest(code=code),
                    Image.open(output_dir / f"imgs/rooms/{code}.png") as rendered,
                    (
                        Image.open(ROOT / "static" / expected[code]["sourceImagePath"])
                    ) as source,
                ):
                    self.assertNotEqual(
                        rendered.getpixel(target),
                        source.convert("RGB").getpixel(target),
                    )
                    self.assertEqual(
                        rendered.getpixel(neighbor),
                        source.convert("RGB").getpixel(neighbor),
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
            for code in PILOT_CODES | {"5201", "GT-A401", "GH-104"}:
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

    def test_rejects_source_image_size_changes(self) -> None:
        annotations = json.loads(
            (ROOT / "static" / "room_map_annotations.json").read_text(encoding="utf-8")
        )
        annotations["maps"][0]["sourceImageSize"] = [1, 1]
        with tempfile.TemporaryDirectory() as temporary_dir:
            annotation_path = Path(temporary_dir) / "annotations.json"
            annotation_path.write_text(json.dumps(annotations), encoding="utf-8")
            with self.assertRaises(RoomMapError):
                build_room_maps(
                    ROOT / "static",
                    Path(temporary_dir) / "output",
                    annotations_path=annotation_path,
                )


if __name__ == "__main__":
    unittest.main()
