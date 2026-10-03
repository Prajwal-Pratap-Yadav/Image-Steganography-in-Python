# StegoLab 0.1.2 engineering preview

Install the wheel with Python 3.11+ (`python -m pip install /path/to/stegolab-0.1.2-py3-none-any.whl`),
or use the repository's hash-locked `make setup`. `stegolab --help` lists file-oriented commands.
No PyPI publication is performed. Linux CI checks Python 3.11/3.12 and an independently installed wheel.

This patch separates the runtime CLI installation from developer tooling. Use `make setup` for the CLI demo
and `make setup-dev` before tests, reproduction, packaging or security scans. Both paths retain hash verification
and preserve an existing virtual environment. Installation time depends on network speed and package caches.

The toolkit provides lossless PNG framing, binary independent extraction, bounded input/output behavior, optional AES-256-GCM/scrypt,
separately keyed ordering, authentication and reproducible synthetic image distortion/pair analysis.
Wheel, source archive and public measurements ZIP are provided with SHA256SUMS.

The measurement manifest identifies the clean experiment source, environment and exact config. These synthetic figures
do not establish natural-image detection accuracy or concealment. LSB is vulnerable to steganalysis and lossy recompression;
steganography is not encryption. Windows runtime, independent format review and licensed natural-image evaluation remain open.
Historical unlicensed sample assets were removed from the current tree; existing history is unchanged.
