import json
import os
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, PngImagePlugin

from stegolab.cli import password_file
from stegolab.errors import StegoError
from stegolab.imageio import load_png, read_limited, save_png


def cli(*args):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    return subprocess.run(
        [sys.executable, "-m", "stegolab", *map(str, args)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_independent_encrypted_disk_roundtrip_and_refuse_overwrite(tmp_path):
    cover, msg, out, decoded, pw = [
        tmp_path / n for n in ("c.png", "m.bin", "s.png", "d.bin", "pw.txt")
    ]
    save_png(cover, np.zeros((32, 32, 4), dtype=np.uint8))
    msg.write_bytes(bytes(range(256)))
    pw.write_text("public-test-passphrase\n")
    assert (
        cli("embed", cover, msg, out, "--encrypt", "--keyed", "--password-file", pw).returncode == 0
    )
    assert cli("extract", out, decoded, "--password-file", pw).returncode == 0
    assert decoded.read_bytes() == msg.read_bytes()
    assert cli("extract", out, decoded, "--password-file", pw).returncode == 2
    assert decoded.read_bytes() == msg.read_bytes()
    pw.write_text("wrong-password")
    failed = tmp_path / "failed.bin"
    assert cli("extract", out, failed, "--password-file", pw).returncode == 2
    assert not failed.exists()
    assert json.loads(cli("capacity", cover).stdout)["capacity_bytes"] > 0


def test_png_modes_metadata_and_lossy_rejection(tmp_path):
    source = tmp_path / "source.png"
    pixels = np.random.default_rng(2).integers(0, 256, (32, 32, 4), dtype=np.uint8)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("private-location", "synthetic metadata fixture")
    Image.fromarray(pixels).save(source, pnginfo=metadata)
    loaded = load_png(source)
    target = tmp_path / "new.png"
    save_png(target, loaded)
    np.testing.assert_array_equal(loaded, pixels)
    with Image.open(target) as im:
        assert "private-location" not in im.info
        assert not im.getexif()
    with pytest.raises(FileExistsError):
        save_png(target, loaded)
    for mode, suffix in [("L", "png"), ("P", "png"), ("RGB", "jpg")]:
        p = tmp_path / f"{mode}.{suffix}"
        Image.new(mode, (32, 32)).save(p)
        with pytest.raises(StegoError):
            load_png(p)
    assert cli("capacity", tmp_path / "RGB.jpg").returncode == 2


def test_predecompression_dimensions_pixels_and_animation(tmp_path):
    source = tmp_path / "a.png"
    Image.new("RGB", (32, 32)).save(source)
    original = source.read_bytes()
    for width, height in [(4097, 1), (2048, 2048), (0, 32)]:
        modified = bytearray(original)
        modified[16:24] = struct.pack(">II", width, height)
        source.write_bytes(modified)
        with pytest.raises(StegoError):
            load_png(source)
    Image.new("RGB", (32, 32)).save(
        source, save_all=True, append_images=[Image.new("RGB", (32, 32), color="red")], duration=100
    )
    with pytest.raises(StegoError, match="Animated"):
        load_png(source)
    source.write_bytes(b"too many bytes")
    with pytest.raises(StegoError):
        read_limited(source, 2)
    source.write_bytes(original[:20])
    with pytest.raises(StegoError):
        load_png(source)


def test_password_bounds_and_encoding(tmp_path):
    p = tmp_path / "pw"
    assert password_file(None) is None
    p.write_bytes(b"example-password\r\n")
    assert password_file(p) == "example-password"
    for raw in [b"one\ntwo", b"\xff", b"x" * 1027]:
        p.write_bytes(raw)
        with pytest.raises(StegoError):
            password_file(p)
