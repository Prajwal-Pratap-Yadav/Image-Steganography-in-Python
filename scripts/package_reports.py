"""Package only explicitly listed public evidence and checksum release files."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from stegolab import __version__

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)
files = (
    "reports/metrics.csv",
    "reports/run_manifest.json",
    "reports/steganalysis.json",
    "reports/format.json",
    "reports/figures/steganalysis.png",
    "docs/assets/hero.png",
    "examples/cover.png",
    "examples/message.txt",
)
with ZipFile(
    dist / f"stegolab-{__version__}-measurements.zip", "w", compression=ZIP_DEFLATED
) as archive:
    for name in files:
        archive.write(root / name, arcname=name)
assets = [
    dist / f"stegolab-{__version__}-py3-none-any.whl",
    dist / f"stegolab-{__version__}.tar.gz",
    dist / f"stegolab-{__version__}-measurements.zip",
]
if not all(p.is_file() for p in assets):
    raise SystemExit("Build wheel/source archive before packaging release reports")
(dist / "SHA256SUMS").write_text(
    "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in assets)
)
print("Public release artifacts and SHA256SUMS created.")
