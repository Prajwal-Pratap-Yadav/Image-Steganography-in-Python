"""Resolve local Markdown paths, release versions and exported protocol constants."""

import json
import re
import tomllib
from pathlib import Path

from export_format import specification

from stegolab import __version__

ROOT = Path(__file__).resolve().parents[1]
errors = []
for file in ROOT.rglob("*.md"):
    if any(
        part.startswith(".") or part in ("build", "dist") for part in file.relative_to(ROOT).parts
    ):
        continue
    text = re.sub(r"```.*?```", "", file.read_text(), flags=re.S)
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.split("#")[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        if not (file.parent / target).exists():
            errors.append(f"{file.relative_to(ROOT)}: missing {target}")
metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
if metadata["version"] != __version__:
    errors.append("Package metadata version differs")
for name in ("README.md", "CHANGELOG.md", "CITATION.cff"):
    if __version__ not in (ROOT / name).read_text():
        errors.append(f"{name}: version missing")
if json.loads((ROOT / "reports/format.json").read_text()) != specification():
    errors.append("Format constants differ from implementation; regenerate and review")
for name in ("setup", "lint", "typecheck", "test", "run", "reproduce", "docs", "clean"):
    if not re.search(rf"^{name}:", (ROOT / "Makefile").read_text(), flags=re.M):
        errors.append(f"Missing make target {name}")
if errors:
    raise SystemExit("\n".join(errors))
print("Local documentation links, versions, Make targets and format constants verified.")
