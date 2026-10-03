"""Generate machine-readable normative constants from the implementation."""

import argparse
import json
from pathlib import Path

from stegolab import __version__
from stegolab.codec import MAX_DIMENSION, MAX_PIXELS
from stegolab.header import HEADER_BYTES, HEADER_SLOTS, MAX_PAYLOAD
from stegolab.imageio import MAX_IMAGE_BYTES


def specification():
    return {
        "package_version": __version__,
        "magic": "STGL",
        "format_version": 1,
        "struct": ">4sBBBBQ16s12s32s",
        "header_bytes": HEADER_BYTES,
        "header_slots": HEADER_SLOTS,
        "depths": [1, 2, 4],
        "flags": {"encrypted": 1, "keyed": 2},
        "max_payload_bytes": MAX_PAYLOAD,
        "max_image_bytes": MAX_IMAGE_BYTES,
        "max_pixels": MAX_PIXELS,
        "max_dimension": MAX_DIMENSION,
        "scrypt": {"n": 2**14, "r": 8, "p": 1, "derived_bytes": 96},
        "key_slices": {"aes_gcm": [0, 32], "ordering": [32, 64], "hmac": [64, 96]},
        "aes_gcm_nonce_bytes": 12,
        "aes_gcm_tag_bytes": 16,
        "ordering": (
            "Partial Fisher-Yates; ChaCha20 zero 16-byte initial counter/nonce; "
            "unbiased uint64 LE rejection"
        ),
        "password_utf8_bytes": [8, 1024],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/format.json"))
    path = parser.parse_args().output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(specification(), indent=2) + "\n")
