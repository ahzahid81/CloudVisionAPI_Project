"""Image annotation helpers."""

from __future__ import annotations

from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont

PALETTE = (
    "#FF4B4B",
    "#FF9F1C",
    "#2EC4B6",
    "#3A86FF",
    "#8338EC",
    "#FF006E",
    "#06D6A0",
    "#FB5607",
)
MAX_DISPLAY_SIZE = (1600, 1600)


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def annotate_objects(
    image: Image.Image,
    objects: Iterable[dict[str, Any]],
    palette: tuple[str, ...] = PALETTE,
) -> Image.Image:
    """Return a copy of the image with labelled bounding boxes for detected objects."""
    canvas = image.convert("RGB").copy()
    canvas.thumbnail(MAX_DISPLAY_SIZE, Image.Resampling.LANCZOS)
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)

    line_width = max(2, round(width / 320))
    font = _load_font(max(12, round(width / 60)))
    padding = max(3, round(width / 400))

    for index, obj in enumerate(objects):
        points = [
            (float(x) * width, float(y) * height)
            for x, y in obj.get("box", [])
        ]
        if len(points) < 3:
            continue

        color = palette[index % len(palette)]
        draw.line(points + [points[0]], fill=color, width=line_width, joint="curve")

        name = str(obj.get("name", "object"))
        score = float(obj.get("score", 0.0))
        label = f"{name} {score * 100:.0f}%"
        text_width, text_height = _text_size(draw, label, font)

        x0 = min(point[0] for point in points)
        y0 = min(point[1] for point in points)
        label_y = y0 - text_height - 2 * padding
        if label_y < 0:
            label_y = y0

        draw.rectangle(
            (x0, label_y, x0 + text_width + 2 * padding, label_y + text_height + 2 * padding),
            fill=color,
        )
        draw.text((x0 + padding, label_y + padding), label, fill="white", font=font)

    return canvas
