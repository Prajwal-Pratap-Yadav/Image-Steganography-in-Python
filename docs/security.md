# Threat model

LSB is not secure against steganalysis. Lossy recompression destroys stored bits. Steganography is not encryption.
Use consented educational experiments, respect image rights, and do not use this for exfiltration or abuse.

| Threat | Implemented behavior | Remaining limit |
|---|---|---|
| Format-aware observer | Visible framing and documented analysis | No deniability guarantee |
| Corruption/wrong password | Plain SHA; keyed HMAC; library GCM | Plain hashes are forgeable; password guessing remains |
| Malicious image/header | Pre-decompression bounds; body bounded before KDF | Image library surface; no sandbox guarantee |
| Destructive output | Exclusive new-file writes | Disk failure can leave a partial new file |
| Metadata disclosure | New PNG from pixels without source EXIF/GPS | Visible content can disclose information |
| Local password exposure | File input, no value in arguments/output | OS permissions and process memory remain owner's responsibility |

Keyed ordering distributes changes; it does not encrypt plaintext. The format has not had independent cryptographic review.
Public benchmark passwords/salts are fixtures, not credentials. No general detector evaluation has been performed.
Bounds are in [format JSON](../reports/format.json). Original legacy code is unmaintained and not runtime.
Report privately via [SECURITY](../SECURITY.md); do not post live secrets publicly.
