from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


class RoomMapError(ValueError):
    """Raised when the room-map annotations or source assets are invalid."""


ROOM_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9-]*$")
ANNOTATION_FILENAME = "room_map_annotations.json"
MANIFEST_FILENAME = "room_maps.json"
ROOM_OUTPUT_DIR = Path("imgs") / "rooms"
HIGHLIGHT_FILL = (224, 58, 58, 96)
HIGHLIGHT_OUTLINE = (183, 24, 24, 255)
HIGHLIGHT_WIDTH = 8


def _relative_path(value: Any, *, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise RoomMapError(f"{field} must be a non-empty path string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise RoomMapError(f"{field} must be relative to the static root: {value!r}")
    return path


def _load_annotations(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RoomMapError(
            f"Unable to read room-map annotations {path}: {error}"
        ) from error

    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise RoomMapError(f"Room-map annotations {path} must have version 1")
    maps = payload.get("maps")
    if not isinstance(maps, list) or not maps:
        raise RoomMapError(
            f"Room-map annotations {path} must contain a non-empty maps list"
        )
    return maps


def _parse_polygon(value: Any, *, code: str) -> list[tuple[int, int]]:
    if not isinstance(value, list) or len(value) < 3:
        raise RoomMapError(f"Room {code} polygon must contain at least three points")

    points: list[tuple[int, int]] = []
    for point in value:
        if (
            not isinstance(point, list)
            or len(point) != 2
            or not all(
                isinstance(coordinate, int) and not isinstance(coordinate, bool)
                for coordinate in point
            )
        ):
            raise RoomMapError(
                f"Room {code} polygon points must be integer [x, y] pairs"
            )
        points.append((point[0], point[1]))
    return points


def _polygon_area(points: list[tuple[int, int]]) -> float:
    return abs(
        sum(
            x1 * y2 - x2 * y1
            for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1], strict=True)
        )
        / 2
    )


def _validate_polygon(
    points: list[tuple[int, int]], *, code: str, image_size: tuple[int, int]
) -> None:
    width, height = image_size
    if any(x < 0 or x >= width or y < 0 or y >= height for x, y in points):
        raise RoomMapError(f"Room {code} polygon is outside source image bounds")
    if _polygon_area(points) == 0:
        raise RoomMapError(f"Room {code} polygon has zero area")


def _validate_map(
    map_entry: Any,
    *,
    source_root: Path,
    seen_codes: set[str],
) -> tuple[str, str, Path, list[tuple[str, list[tuple[int, int]]]]]:
    if not isinstance(map_entry, dict):
        raise RoomMapError("Every room-map entry must be an object")

    building = map_entry.get("building")
    floor = map_entry.get("floor")
    if not isinstance(building, str) or not building:
        raise RoomMapError("Room-map building must be a non-empty string")
    if not isinstance(floor, str) or not floor:
        raise RoomMapError(
            f"Room-map floor for {building!r} must be a non-empty string"
        )

    source_path = _relative_path(
        map_entry.get("sourceImagePath"), field="sourceImagePath"
    )
    source_file = source_root / source_path
    if not source_file.is_file():
        raise RoomMapError(f"Room-map source image does not exist: {source_path}")
    try:
        with Image.open(source_file) as source_image:
            image_size = source_image.size
    except (OSError, Image.DecompressionBombError) as error:
        raise RoomMapError(
            f"Unable to open room-map source image {source_path}: {error}"
        ) from error

    expected_size = map_entry.get("sourceImageSize")
    if (
        not isinstance(expected_size, list)
        or len(expected_size) != 2
        or not all(
            isinstance(dimension, int) and not isinstance(dimension, bool)
            for dimension in expected_size
        )
        or tuple(expected_size) != image_size
    ):
        raise RoomMapError(
            f"Room-map source image size for {source_path} must match "
            f"{image_size[0]}x{image_size[1]}"
        )

    rooms = map_entry.get("rooms")
    if not isinstance(rooms, list) or not rooms:
        raise RoomMapError(f"Room-map {building} floor {floor} must contain rooms")

    parsed_rooms: list[tuple[str, list[tuple[int, int]]]] = []
    for room in rooms:
        if not isinstance(room, dict):
            raise RoomMapError("Every room annotation must be an object")
        code = room.get("code")
        if not isinstance(code, str) or not ROOM_CODE_PATTERN.fullmatch(code):
            raise RoomMapError(f"Invalid room code: {code!r}")
        if code in seen_codes:
            raise RoomMapError(f"Duplicate room code in room-map annotations: {code}")
        polygon = _parse_polygon(room.get("polygon"), code=code)
        _validate_polygon(polygon, code=code, image_size=image_size)
        seen_codes.add(code)
        parsed_rooms.append((code, polygon))

    return building, floor, source_path, parsed_rooms


def _render_room_map(
    source_file: Path,
    output_file: Path,
    polygon: list[tuple[int, int]],
) -> None:
    with Image.open(source_file) as source:
        image = source.convert("RGBA")

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.polygon(polygon, fill=HIGHLIGHT_FILL)
    outline = polygon + [polygon[0]]
    draw.line(outline, fill=HIGHLIGHT_OUTLINE, width=HIGHLIGHT_WIDTH, joint="curve")
    rendered = Image.alpha_composite(image, overlay).convert("RGB")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    rendered.save(output_file, format="PNG", compress_level=9)


def build_room_maps(
    source_root: Path,
    output_root: Path,
    *,
    annotations_path: Path | None = None,
) -> Path:
    """Validate annotations and render one highlighted floor map per room.

    ``source_root`` contains checked-in floor maps and annotations. ``output_root``
    receives the published ``room_maps.json`` manifest and generated images.
    """

    source_root = source_root.resolve()
    output_root = output_root.resolve()
    annotation_file = annotations_path or source_root / ANNOTATION_FILENAME
    annotation_file = annotation_file.resolve()
    maps = _load_annotations(annotation_file)
    output_dir = output_root / ROOM_OUTPUT_DIR
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    seen_codes: set[str] = set()
    records: list[dict[str, object]] = []

    for map_entry in maps:
        building, floor, source_path, rooms = _validate_map(
            map_entry,
            source_root=source_root,
            seen_codes=seen_codes,
        )
        source_file = source_root / source_path
        with Image.open(source_file) as source_image:
            image_size = source_image.size
        for code, polygon in rooms:
            image_path = ROOM_OUTPUT_DIR / f"{code}.png"
            _validate_polygon(polygon, code=code, image_size=image_size)
            _render_room_map(source_file, output_root / image_path, polygon)
            records.append(
                {
                    "code": code,
                    "building": building,
                    "floor": floor,
                    "imagePath": image_path.as_posix(),
                    "sourceImagePath": source_path.as_posix(),
                }
            )

    records.sort(key=lambda record: str(record["code"]))
    manifest_path = output_root / MANIFEST_FILENAME
    manifest_path.write_text(
        json.dumps({"rooms": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build highlighted room floor maps")
    parser.add_argument("--source-dir", type=Path, default=Path("static"))
    parser.add_argument("--output-dir", type=Path, default=Path("build"))
    parser.add_argument("--annotations", type=Path)
    args = parser.parse_args()
    manifest_path = build_room_maps(
        args.source_dir,
        args.output_dir,
        annotations_path=args.annotations,
    )
    print(f"Generated room-map manifest: {manifest_path}")


if __name__ == "__main__":
    main()
