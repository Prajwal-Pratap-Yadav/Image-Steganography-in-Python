from dataclasses import replace

import numpy as np
import pytest

from stegolab.codec import _values, embed, extract
from stegolab.errors import StegoError
from stegolab.header import HEADER_SLOTS, STRUCT, Header


@pytest.mark.parametrize("encrypted,keyed", [(True, False), (True, True), (False, True)])
def test_valid_metadata_tamper_fails_authentication(encrypted, keyed):
    password = "public-fixture-passphrase"
    image = embed(
        np.zeros((40, 40, 3), dtype=np.uint8),
        b"payload",
        encrypted=encrypted,
        keyed=keyed,
        password=password,
    )
    image.reshape(-1)[16 * 8] ^= 1  # structurally valid salt modification
    with pytest.raises(StegoError):
        extract(image, password=password)


def test_declared_capacity_rejected_before_password_derivation(monkeypatch):
    image = np.zeros((32, 32, 3), dtype=np.uint8)
    header = Header(1, 1, 524288 + 16).pack()
    image.reshape(-1)[:HEADER_SLOTS] = _values(header, 1)
    monkeypatch.setattr(
        "stegolab.codec.derive", lambda *_: pytest.fail("KDF called for impossible length")
    )
    with pytest.raises(StegoError, match="capacity"):
        extract(image, password="public-fixture-passphrase")


@pytest.mark.parametrize("field,value", [(0, b"NOPE"), (1, 2), (4, 1), (3, 128)])
def test_unknown_header_fields(field, value):
    fields = list(STRUCT.unpack(Header(1, 0, 0).pack()))
    fields[field] = value
    with pytest.raises(StegoError):
        Header.unpack(STRUCT.pack(*fields))


def test_encrypted_empty_requires_tag_space():
    tiny = np.zeros((1, 203, 3), dtype=np.uint8)  # 609 channels: header fits, tag cannot
    with pytest.raises(StegoError, match="capacity"):
        embed(tiny, b"", encrypted=True, password="public-fixture-passphrase")
    with pytest.raises(StegoError):
        replace(Header(1, 1, 16), digest=b"x" * 32).pack()
