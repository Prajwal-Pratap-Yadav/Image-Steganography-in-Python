# Changelog

Keep a Changelog conventions; versions describe this package, not historical scripts.

## [0.1.2] - 2026-10-03

### Changed

- The CLI quickstart installs only hash-locked runtime packages and build prerequisites.
- `make setup-dev` adds developer tools, the verified scanner and staged hooks; CI uses this complete environment.
- The bootstrap lock has a small pinned source file for reproducible regeneration.

## [0.1.1] - 2026-10-03

### Fixed

- Repeated setup preserves the existing virtual environment instead of overlaying its pinned pip installation.
- Hash-locked development packages are copied into the environment, keeping dependency auditing isolated from shared caches.

## [0.1.0] - 2026-10-03

### Added

- Lossless framing, independent file CLI, bounded reads, alpha preservation and stripped metadata.
- Optional AES-GCM/scrypt, separately keyed slot ordering and keyed plaintext authentication.
- Reproducible synthetic metrics/figures, tests, locked tooling, format and evidence, CI/release automation.

### Changed

- Preserved original script under legacy; corrected claims; retired unlicensed assets from the current tree.

### Known limits

- No licensed natural-image evaluation, independent review or Windows runtime verification.
