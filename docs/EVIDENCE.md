# Evidence

Measured source f751b2ac65143582f2eed2009a4b0990311af08a, 2026-10-03 UTC.
Command `PYTHONPATH=src python scripts/reproduce.py` (same experiment as `make reproduce`). Linux x86_64, Python3.12.14;
versions, config/hash and CPU information in the manifest.

| Claim | Value | Command | SHA/date | Environment | Artifact |
|---|---|---|---|---|---|
| Synthetic sequential/keyed capacity, PSNR, SSIM | README rounded CSV rows | `make reproduce` | f751b2a / 2026-10-03 | manifest | [CSV](../reports/metrics.csv) |
| Capacity bits/pixel and process time | Exact columns; no throughput claim | `make reproduce` | f751b2a / 2026-10-03 | manifest | [CSV](../reports/metrics.csv) |
| Pair equality/histograms | Global and block values; no accuracy | `make reproduce` | f751b2a / 2026-10-03 | manifest | [JSON](../reports/steganalysis.json) |
| Figure authenticity | Actual generated/saved images and statistics | `make reproduce` | f751b2a / 2026-10-03 | manifest | [hero](assets/hero.png), [plot](../reports/figures/steganalysis.png) |
| Fresh public-clone CLI quickstart | 53.905 s including clone | `git clone --branch portfolio-overhaul`; `UV_CACHE_DIR=<empty> PIP_NO_CACHE_DIR=1 make setup`; `make run` | d7cdbc4 / 2026-10-03 UTC | Linux/Python and cache state in artifact | [quality gates](../reports/quality-gates.json) |
| Protocol sizes/bounds/KDF | Normative, not estimates | `python scripts/export_format.py`; `make docs` | current source / format | format tests | [format.json](../reports/format.json) |

Measurements precede tooling/docs changes. Verification outputs live in ignored reports/local and CI artifacts.
No stable test-count or coverage percentage is advertised. Release/CI must be externally verified before recording completion.
No detection accuracy, natural-image performance, reviewed security or Windows runtime result is claimed.

The quickstart timing covers runtime installation, not developer setup. It is a single measured environment and is not a universal timing promise. The initial full developer quickstart took 75.464 s here; cache state differs and the two observations are not an isolated causal benchmark.
