"""Fixed binary format; no attacker-selected KDF parameters."""

import struct
from dataclasses import dataclass

from .errors import StegoError

STRUCT = struct.Struct(">4sBBBBQ16s12s32s")
HEADER_BYTES = STRUCT.size
HEADER_SLOTS = HEADER_BYTES * 8
MAX_PAYLOAD = 512 * 1024
ENCRYPTED = 1
KEYED = 2


@dataclass(frozen=True)
class Header:
    depth: int
    flags: int
    length: int
    salt: bytes = bytes(16)
    nonce: bytes = bytes(12)
    digest: bytes = bytes(32)

    def validate(self) -> None:
        if self.depth not in (1, 2, 4) or self.flags & ~(ENCRYPTED | KEYED):
            raise StegoError("Unsupported depth or flags")
        tag = 16 if self.flags & ENCRYPTED else 0
        if not tag <= self.length <= MAX_PAYLOAD + tag:
            raise StegoError("Payload length outside limits")
        if len(self.salt) != 16 or len(self.nonce) != 12 or len(self.digest) != 32:
            raise StegoError("Invalid metadata size")
        if not self.flags and self.salt != bytes(16):
            raise StegoError("Unexpected salt")
        if not self.flags & ENCRYPTED and self.nonce != bytes(12):
            raise StegoError("Unexpected nonce")
        if self.flags & ENCRYPTED and self.digest != bytes(32):
            raise StegoError("Unexpected encrypted digest")

    def pack(self) -> bytes:
        self.validate()
        return STRUCT.pack(
            b"STGL",
            1,
            self.depth,
            self.flags,
            0,
            self.length,
            self.salt,
            self.nonce,
            self.digest,
        )

    @classmethod
    def unpack(cls, raw: bytes) -> "Header":
        if len(raw) != HEADER_BYTES:
            raise StegoError("Truncated header")
        magic, version, depth, flags, reserved, length, salt, nonce, digest = STRUCT.unpack(raw)
        if magic != b"STGL" or version != 1 or reserved != 0:
            raise StegoError("Unknown payload format")
        h = cls(depth, flags, length, salt, nonce, digest)
        h.validate()
        return h
