import builtins
import os
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def legacy(monkeypatch, msg, password="sample-pass", size=8):
    image = np.zeros((size, size, 3), dtype=np.uint8)
    written = []
    responses = iter((msg, "sample-pass", password))
    monkeypatch.setattr(builtins, "input", lambda _: next(responses))
    monkeypatch.setattr(os, "system", lambda _: 0)
    monkeypatch.setitem(
        sys.modules,
        "cv2",
        SimpleNamespace(imread=lambda _: image, imwrite=lambda *a: written.append(a)),
    )
    runpy.run_path(str(Path(__file__).parents[1] / "legacy/stego.py"))
    return image, written


def test_in_memory_diagonal_roundtrip(monkeypatch, capsys):
    image, written = legacy(monkeypatch, "abc")
    assert [image[i, i, i % 3] for i in range(3)] == list(b"abc")
    assert written[0][0] == "encryptedImage.jpeg"
    assert "Decryption message: abc" in capsys.readouterr().out


def test_passcode_is_only_local_comparison(monkeypatch, capsys):
    legacy(monkeypatch, "abc", password="different")
    assert "YOU ARE NOT auth" in capsys.readouterr().out


def test_unicode_and_capacity_are_unhandled(monkeypatch):
    with pytest.raises(KeyError):
        legacy(monkeypatch, "🌱")
    with pytest.raises(IndexError):
        legacy(monkeypatch, "too long", size=2)
