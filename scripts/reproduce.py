"""Generate synthetic fixtures, run actual PNG round trips and plot measured values."""

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from stegolab.analysis import analyze_image, distortion
from stegolab.codec import capacity, embed, extract

ROOT = Path(__file__).resolve().parents[1]


def revision():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "source-archive-without-git"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT)
    args = parser.parse_args()
    cfg = json.loads((ROOT / "configs/benchmark.json").read_text())
    rng = np.random.default_rng(cfg["seed"])
    height, width = cfg["height"], cfg["width"]
    y, x = np.indices((height, width))
    # Deliberately even-valued smooth field: a clear pedagogical null comparison.
    cover = (
        np.stack(((x + y) % 128, (x * 2 + y) // 3 % 128, (y * 2 + x) // 3 % 128), axis=2).astype(
            np.uint8
        )
        * 2
    )
    payload = rng.integers(0, 256, cfg["payload_bytes"], dtype=np.uint8).tobytes()
    out = args.output
    for name in ("reports/figures", "docs/assets", "examples"):
        (out / name).mkdir(parents=True, exist_ok=True)
    Image.fromarray(cover).save(out / "examples/cover.png")
    (out / "examples/message.txt").write_text("Public demonstration payload.\n")
    rows = []
    analysis = {"cover": analyze_image(cover)}
    images = {}
    for depth in cfg["depths"]:
        for keyed in (False, True):
            name = f"depth{depth}-" + ("keyed" if keyed else "sequential")
            start = time.perf_counter()
            # Reproducible public fixture ONLY. Library/CLI use fresh OS entropy.
            with patch(
                "stegolab.codec.secrets.token_bytes",
                side_effect=lambda n: rng.integers(0, 256, n, dtype=np.uint8).tobytes(),
            ):
                stego = embed(
                    cover,
                    payload,
                    depth,
                    keyed=keyed,
                    password="public-benchmark-passphrase" if keyed else None,
                )
            path = out / f"reports/figures/{name}.png"
            Image.fromarray(stego).save(path)
            saved = np.array(Image.open(path))
            assert (
                extract(saved, password="public-benchmark-passphrase" if keyed else None) == payload
            )
            elapsed = time.perf_counter() - start
            metrics = distortion(cover, saved)
            rows.append(
                {
                    "depth": depth,
                    "ordering": "keyed" if keyed else "sequential",
                    "capacity_bytes": capacity(cover, depth),
                    "effective_capacity_bpp": capacity(cover, depth) * 8 / (height * width),
                    "payload_bytes": len(payload),
                    **metrics,
                    "roundtrip_seconds": elapsed,
                }
            )
            analysis[name] = analyze_image(saved)
            images[name] = saved
    with (out / "reports/metrics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "git_sha": revision(),
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu": platform.processor()
        or next(
            (
                line.split(":", 1)[1].strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            ),
            "unknown",
        )
        if Path("/proc/cpuinfo").exists()
        else "unknown",
        "logical_cpus": os.cpu_count(),
        "config": cfg,
        "config_sha256": hashlib.sha256((ROOT / "configs/benchmark.json").read_bytes()).hexdigest(),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "versions": {
            p: importlib.metadata.version(p)
            for p in ("numpy", "Pillow", "cryptography", "scipy", "scikit-image", "matplotlib")
        },
        "scope": "Synthetic even-valued cover; exploratory statistics, no detector accuracy.",
    }
    (out / "reports/run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (out / "reports/steganalysis.json").write_text(
        json.dumps(analysis, indent=2, allow_nan=False) + "\n"
    )
    plt.style.use("dark_background")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), layout="constrained")
    seq = images["depth1-sequential"]
    diff = np.clip(np.abs(cover.astype(int) - seq.astype(int)) * 32, 0, 255).astype(np.uint8)
    for ax, im, title in zip(
        axes,
        (cover, seq, diff),
        ("Generated cover", "Payload in PNG", "Absolute difference ×32"),
        strict=True,
    ):
        ax.imshow(im)
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle("StegoLab · measured synthetic demonstration")
    fig.savefig(out / "docs/assets/hero.png", dpi=150)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    for name in ("cover", "depth1-sequential", "depth1-keyed"):
        blocks = analysis[name]["row_blocks"]
        axes[0].plot(
            [b["start_row"] for b in blocks],
            [b["normalized_statistic"] for b in blocks],
            label=name,
        )
        hist = np.array(analysis[name]["global"]["histogram"])
        axes[1].plot(hist[::2] - hist[1::2], label=name)
    axes[0].set(xlabel="Start row", ylabel="Pair chi-square / active pairs")
    axes[1].set(xlabel="Even/odd pair index", ylabel="Even count − odd count")
    for ax in axes:
        ax.legend()
        ax.grid(alpha=0.2)
    fig.savefig(out / "reports/figures/steganalysis.png", dpi=150)
    plt.close(fig)
    print(json.dumps({"output": str(out), "cases": len(rows), "source": manifest["git_sha"]}))


if __name__ == "__main__":
    main()
