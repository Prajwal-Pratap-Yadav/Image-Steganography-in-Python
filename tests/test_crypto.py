import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from stegolab.codec import embed, extract
from stegolab.crypto import derive, slots
from stegolab.errors import StegoError
from stegolab.header import HEADER_SLOTS

PASSWORD = "public-test-passphrase"


@pytest.mark.parametrize("depth", [1, 2, 4])
@pytest.mark.parametrize(
    "encrypted,keyed", [(True, False), (False, True), (True, True)]
)
def test_modes_and_wrong_password(depth, encrypted, keyed):
    im = np.zeros((32, 32, 4), dtype=np.uint8)
    im[:, :, 3] = 127
    out = embed(
        im, b"\x00\xff\x01", depth, password=PASSWORD, encrypted=encrypted, keyed=keyed
    )
    assert extract(out, password=PASSWORD) == b"\x00\xff\x01"
    assert np.array_equal(out[:, :, 3], im[:, :, 3])
    with pytest.raises(StegoError):
        extract(out, password="wrong-password")
    with pytest.raises(StegoError):
        extract(out)


@settings(max_examples=12, derandomize=True, deadline=None)
@given(st.binary(max_size=80), st.sampled_from([1, 2, 4]))
def test_encrypted_property(payload, depth):
    im = np.zeros((32, 32, 3), dtype=np.uint8)
    assert (
        extract(
            embed(im, payload, depth, password=PASSWORD, encrypted=True, keyed=True),
            password=PASSWORD,
        )
        == payload
    )


@pytest.mark.parametrize("payload", [b"", bytes(32), bytes([255]) * 32])
def test_keyed_constant_payload_authenticates_password(payload):
    out = embed(
        np.zeros((32, 32, 3), dtype=np.uint8), payload, keyed=True, password=PASSWORD
    )
    with pytest.raises(StegoError):
        extract(out, password="wrong-password")


def test_entropy_tamper_and_separate_keys():
    im = np.zeros((32, 32, 3), dtype=np.uint8)
    a = embed(im, b"hello", encrypted=True, password=PASSWORD)
    b = embed(im, b"hello", encrypted=True, password=PASSWORD)
    assert not np.array_equal(a, b)
    a.reshape(-1)[HEADER_SLOTS] ^= 1
    with pytest.raises(StegoError, match="authentication"):
        extract(a, password=PASSWORD)
    c = embed(im, b"hello", encrypted=True, password=PASSWORD)
    c.reshape(-1)[5 * 8 + 7] ^= 1  # depth 1 -> 0: malformed header rejected
    with pytest.raises(StegoError):
        extract(c, password=PASSWORD)
    keys = derive(PASSWORD, bytes(16))
    assert len(set(keys)) == 3
    chosen = slots(100, 100, keys[1])
    assert len(set(chosen)) == 100
    np.testing.assert_array_equal(chosen, slots(100, 100, keys[1]))
    for password in ("tiny", "x" * 1025):
        with pytest.raises(StegoError):
            derive(password, bytes(16))
    with pytest.raises(StegoError):
        embed(im, b"hello", password=PASSWORD)
