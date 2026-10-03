"""Bound bytes and dimensions before PNG decompression; never carry metadata."""

import io
import os
import struct
from pathlib import Path

import numpy as np
from PIL import Image

from .codec import MAX_DIMENSION, MAX_PIXELS, ImageArray, validate_image
from .errors import StegoError

MAX_IMAGE_BYTES = 8 * 1024 * 1024


def read_limited(path: Path, limit: int) -> bytes:
    with path.open("rb") as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise StegoError("File exceeds byte limit")
    return raw


def load_png(path: Path) -> ImageArray:
    raw = read_limited(path, MAX_IMAGE_BYTES)
    if len(raw) < 33 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise StegoError("Only lossless PNG input is supported; JPEG is rejected")
    width, height, depth, color = struct.unpack(">IIBB", raw[16:26])
    if not (0 < width <= MAX_DIMENSION and 0 < height <= MAX_DIMENSION):
        raise StegoError("PNG dimensions outside limits")
    if width * height > MAX_PIXELS:
        raise StegoError("PNG exceeds pixel limit")
    if depth != 8 or color not in (2, 6):
        raise StegoError("Only 8-bit RGB or RGBA PNG is supported")
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if getattr(image, "is_animated", False):
                raise StegoError("Animated PNG is unsupported")
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            array = np.array(image, dtype=np.uint8)
    except StegoError:
        raise
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombError) as exc:
        raise StegoError("Invalid PNG or oversized metadata") from exc
    validate_image(array)
    return array


def write_new(path: Path, raw: bytes) -> None:
    # O_EXCL also refuses an existing symlink; never truncate a user file.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)


def save_png(path: Path, image: ImageArray) -> None:
    validate_image(image)
    if path.suffix.lower() != ".png":
        raise StegoError("Output image must use a .png extension")
    buffer = io.BytesIO()
    Image.fromarray(image).save(buffer, format="PNG")
    write_new(path, buffer.getvalue())
