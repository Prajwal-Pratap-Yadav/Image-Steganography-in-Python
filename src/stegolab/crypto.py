"""Library AEAD and independent derived keys for channel ordering and MAC."""

import struct
from collections.abc import Iterator

import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from numpy.typing import NDArray

from .errors import StegoError


def derive(password: str | None, salt: bytes) -> tuple[bytes, bytes, bytes]:
    if password is None:
        raise StegoError("A password file is required for this payload")
    raw = password.encode("utf-8")
    if not 8 <= len(raw) <= 1024:
        raise StegoError("Password must contain 8–1024 UTF-8 bytes")
    material = Scrypt(salt=salt, length=96, n=2**14, r=8, p=1).derive(raw)
    return material[:32], material[32:64], material[64:]


def _words(key: bytes) -> Iterator[int]:
    # Each derivation has a fresh salt and thus a fresh ordering key.
    stream = Cipher(algorithms.ChaCha20(key, bytes(16)), mode=None).encryptor()
    while True:
        for (word,) in struct.iter_unpack("<Q", stream.update(bytes(4096))):
            yield word


def slots(total: int, count: int, key: bytes | None) -> NDArray[np.int64]:
    if not 0 <= count <= total:
        raise StegoError("Slot count outside capacity")
    remaining = np.arange(total, dtype=np.int64)
    if key is not None:
        words = _words(key)
        for i in range(count):
            bound = total - i
            limit = 2**64 - (2**64 % bound)
            word = next(words)
            while word >= limit:
                word = next(words)
            j = i + word % bound
            remaining[i], remaining[j] = remaining[j], remaining[i]
    return remaining[:count]
