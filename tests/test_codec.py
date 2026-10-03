import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stegolab.codec import capacity, embed, extract
from stegolab.errors import StegoError
from stegolab.header import HEADER_SLOTS, Header


@pytest.mark.parametrize("depth", [1, 2, 4])
def test_exact_capacity_alpha_and_overflow(depth):
    im = np.random.default_rng(9).integers(0, 256, (32, 32, 4), dtype=np.uint8)
    payload = bytes(capacity(im, depth))
    out = embed(im, payload, depth)
    assert extract(out) == payload
    np.testing.assert_array_equal(im[:, :, 3], out[:, :, 3])
    np.testing.assert_array_equal(im, im.copy())
    with pytest.raises(StegoError, match="capacity"):
        embed(im, payload + b"x", depth)


@settings(max_examples=100, derandomize=True, deadline=None)
@given(st.binary(max_size=250), st.integers(28, 80), st.sampled_from([1, 2, 4]))
def test_roundtrip_property(payload, width, depth):
    im = np.random.default_rng(width).integers(0, 256, (32, width, 3), dtype=np.uint8)
    assert extract(embed(im, payload, depth)) == payload


def test_tamper_empty_and_header_limits():
    im = np.zeros((32, 32, 3), dtype=np.uint8)
    assert extract(embed(im, b"")) == b""
    out = embed(im, b"ab")
    out.reshape(-1)[HEADER_SLOTS] ^= 1
    with pytest.raises(StegoError, match="integrity"):
        extract(out)
    for h in (Header(3, 0, 0), Header(1, 8, 0), Header(1, 0, 2**60)):
        with pytest.raises(StegoError):
            h.pack()
    with pytest.raises(StegoError):
        extract(np.zeros((2, 2, 3), dtype=np.uint8))
    with pytest.raises(StegoError):
        capacity(np.zeros((10, 10), dtype=np.uint8))
