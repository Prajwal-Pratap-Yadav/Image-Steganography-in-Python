"""RGB channel low-bit packing. Alpha is never a storage channel."""

import hashlib
import hmac
import secrets
from dataclasses import replace

import numpy as np
from numpy.typing import NDArray
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .crypto import derive, slots
from .errors import StegoError
from .header import ENCRYPTED, KEYED, HEADER_SLOTS, MAX_PAYLOAD, Header

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


def embed(
    image: ImageArray,
    payload: bytes,
    depth: int = 1,
    *,
    password: str | None = None,
    encrypted: bool = False,
    keyed: bool = False,
) -> ImageArray:
    validate_image(image)
    flat = image[:, :, :3].copy().reshape(-1)
    body_length = len(payload) + (16 if encrypted else 0)
    if (
        flat.size < HEADER_SLOTS
        or len(payload) > capacity(image, depth, encrypted)
        or body_length * 8 > (flat.size - HEADER_SLOTS) * depth
    ):
        raise StegoError("Payload exceeds image capacity")
    if password is not None and not (encrypted or keyed):
        raise StegoError("Password requires encryption or keyed ordering")
    flags = (ENCRYPTED if encrypted else 0) | (KEYED if keyed else 0)
    h = Header(
        depth,
        flags,
        body_length,
        secrets.token_bytes(16) if flags else bytes(16),
        secrets.token_bytes(12) if encrypted else bytes(12),
    )
    enc_key, order_key, mac_key = derive(password, h.salt) if flags else (b"", b"", b"")
    if encrypted:
        body = AESGCM(enc_key).encrypt(h.nonce, payload, h.pack())
    else:
        body = payload
        raw = h.pack() + body
        digest = (
            hmac.digest(mac_key, raw, "sha256")
            if keyed
            else hashlib.sha256(raw).digest()
        )
        h = replace(h, digest=digest)
    flat[:HEADER_SLOTS] = (flat[:HEADER_SLOTS] & 254) | _values(h.pack(), 1)
    values = _values(body, depth)
    positions = HEADER_SLOTS + slots(
        flat.size - HEADER_SLOTS, len(values), order_key if keyed else None
    )
    flat[positions] = (flat[positions] & (255 ^ ((1 << depth) - 1))) | values
    out = image.copy()
    out[:, :, :3] = flat.reshape(image.shape[0], image.shape[1], 3)
    return out


def extract(image: ImageArray, *, password: str | None = None) -> bytes:
    validate_image(image)
    flat = image[:, :, :3].copy().reshape(-1)
    if flat.size < HEADER_SLOTS:
        raise StegoError("Image too small for header")
    h = Header.unpack(_bytes(flat[:HEADER_SLOTS], 1))
    count = h.length * 8 // h.depth
    if HEADER_SLOTS + count > flat.size:
        raise StegoError("Declared payload exceeds image capacity")
    if password is not None and not h.flags:
        raise StegoError("Password supplied for an unkeyed plaintext payload")
    enc_key, order_key, mac_key = (
        derive(password, h.salt) if h.flags else (b"", b"", b"")
    )
    positions = HEADER_SLOTS + slots(
        flat.size - HEADER_SLOTS, count, order_key if h.flags & KEYED else None
    )
    payload = _bytes(flat[positions], h.depth)
    if h.flags & ENCRYPTED:
        try:
            return AESGCM(enc_key).decrypt(h.nonce, payload, h.pack())
        except InvalidTag as exc:
            raise StegoError("Password or payload authentication failed") from exc
    raw = replace(h, digest=bytes(32)).pack() + payload
    expected = (
        hmac.digest(mac_key, raw, "sha256")
        if h.flags & KEYED
        else hashlib.sha256(raw).digest()
    )
    if not hmac.compare_digest(h.digest, expected):
        raise StegoError("Payload integrity check failed")
    return payload
