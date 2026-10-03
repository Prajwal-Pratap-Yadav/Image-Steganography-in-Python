"""RGB channel low-bit packing. Alpha is never a storage channel."""

import hashlib
import hmac
from dataclasses import replace

import numpy as np
from numpy.typing import NDArray

from .errors import StegoError
from .header import HEADER_SLOTS, MAX_PAYLOAD, Header

ImageArray = NDArray[np.uint8]
MAX_PIXELS = 1_048_576
MAX_DIMENSION = 4096


def validate_image(image: ImageArray) -> None:
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] not in (3, 4):
        raise StegoError("An 8-bit RGB or RGBA image is required")
    height, width = image.shape[:2]
    if min(height, width) < 1 or max(height, width) > MAX_DIMENSION:
        raise StegoError("Image dimensions outside limits")
    if height * width > MAX_PIXELS:
        raise StegoError("Image exceeds pixel limit")


def capacity(image: ImageArray, depth: int = 1, encrypted: bool = False) -> int:
    validate_image(image)
    if depth not in (1, 2, 4):
        raise StegoError("Depth must be 1, 2 or 4")
    slots = max(0, image.shape[0] * image.shape[1] * 3 - HEADER_SLOTS)
    return max(0, min(MAX_PAYLOAD, slots * depth // 8 - (16 if encrypted else 0)))


def _values(raw: bytes, depth: int) -> ImageArray:
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8))
    weights = (1 << np.arange(depth - 1, -1, -1)).astype(np.uint8)
    return (bits.reshape(-1, depth) @ weights).astype(np.uint8)


def _bytes(values: ImageArray, depth: int) -> bytes:
    shifts = np.arange(depth - 1, -1, -1)
    bits = ((values[:, None] >> shifts) & 1).astype(np.uint8).reshape(-1)
    return np.packbits(bits).tobytes()


def embed(image: ImageArray, payload: bytes, depth: int = 1) -> ImageArray:
    validate_image(image)
    flat = image[:, :, :3].copy().reshape(-1)
    if flat.size < HEADER_SLOTS or len(payload) > capacity(image, depth):
        raise StegoError("Payload exceeds image capacity")
    h = Header(depth, 0, len(payload))
    digest = hashlib.sha256(h.pack() + payload).digest()
    h = replace(h, digest=digest)
    flat[:HEADER_SLOTS] = (flat[:HEADER_SLOTS] & 254) | _values(h.pack(), 1)
    values = _values(payload, depth)
    slots = slice(HEADER_SLOTS, HEADER_SLOTS + len(values))
    flat[slots] = (flat[slots] & (255 ^ ((1 << depth) - 1))) | values
    out = image.copy()
    out[:, :, :3] = flat.reshape(image.shape[0], image.shape[1], 3)
    return out


def extract(image: ImageArray) -> bytes:
    validate_image(image)
    flat = image[:, :, :3].copy().reshape(-1)
    if flat.size < HEADER_SLOTS:
        raise StegoError("Image too small for header")
    h = Header.unpack(_bytes(flat[:HEADER_SLOTS], 1))
    if h.flags:
        raise StegoError("Password modes unavailable")
    count = h.length * 8 // h.depth
    if HEADER_SLOTS + count > flat.size:
        raise StegoError("Declared payload exceeds image capacity")
    payload = _bytes(flat[HEADER_SLOTS : HEADER_SLOTS + count], h.depth)
    expected = hashlib.sha256(replace(h, digest=bytes(32)).pack() + payload).digest()
    if not hmac.compare_digest(h.digest, expected):
        raise StegoError("Payload integrity check failed")
    return payload
