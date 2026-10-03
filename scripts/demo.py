"""Actual separate-process encrypted/keyed disk round trip on generated input."""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("reports/local/demo"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        root = Path(work)
        cover, payload, secret, stego, decoded = (
            root / name for name in ("cover.png", "payload.bin", "pw", "stego.png", "decoded.bin")
        )
        Image.fromarray(
            np.random.default_rng(1).integers(0, 256, (64, 64, 3), dtype=np.uint8)
        ).save(cover)
        payload.write_bytes(b"Public demonstration.\n")
        secret.write_text("public-demo-passphrase")
        for command in (
            ["capacity", str(cover)],
            [
                "embed",
                str(cover),
                str(payload),
                str(stego),
                "--encrypt",
                "--keyed",
                "--password-file",
                str(secret),
            ],
            ["extract", str(stego), str(decoded), "--password-file", str(secret)],
            ["analyze", str(stego), "--cover", str(cover)],
        ):
            result = subprocess.run(
                [sys.executable, "-m", "stegolab", *command],
                check=True,
                capture_output=True,
                text=True,
            )
            print(result.stdout.strip())
            if command[0] == "analyze":
                (args.output / "analysis.json").write_text(result.stdout)
        assert payload.read_bytes() == decoded.read_bytes()
        Image.open(stego).save(args.output / "stego.png")
    print("Independent disk round trip verified.")


if __name__ == "__main__":
    main()
