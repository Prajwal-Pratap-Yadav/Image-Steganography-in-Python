# STGL format v1

Normative numeric constants: [generated JSON](../reports/format.json), exported from runtime via
`python scripts/export_format.py`. Binary struct: `>4sBBBBQ16s12s32s`.

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 4 | ASCII STGL |
| 4 | 1 | Version, 1 |
| 5 | 1 | Body bits/channel: 1 / 2 / 4 |
| 6 | 1 | Flags: encrypted=1, keyed=2 |
| 7 | 1 | Reserved, zero |
| 8 | 8 | Big-endian stored body length |
| 16 | 16 | scrypt salt |
| 32 | 12 | AES-GCM nonce |
| 44 | 32 | SHA-256 / HMAC; zero when encrypted |

Header occupies the first 608 RGB channels, row-major, one least significant bit each, MSB-first bytes.
Alpha is excluded. Body uses low-bit groups of selected depth, MSB group order, with no terminator.
Capacity = max(0, min(payload bound, floor(max(0,3×pixels−608)×depth/8)−tag)); tag=16 for encryption.
Header/tag must physically fit, including empty payloads.

Sequential bodies use following slots. Keyed bodies use partial Fisher–Yates over ascending remaining slot indices:
draw an unbiased remaining index, swap, select prefix. ChaCha20 under the dedicated ordering key starts at all-zero
16-byte counter/nonce; read unsigned little-endian 64-bit words. Reject words ≥ `2^64−(2^64 mod remaining)` before reduction.
Fresh salt gives a fresh ordering key; format does not rely on NumPy permutation versions.

scrypt N=16384, r=8, p=1 derives 96 bytes: first 32 AES key, next 32 ordering key, last 32 HMAC key.
Plain SHA-256 covers zero-digest header || body. Keyed plaintext uses HMAC-SHA256 on that input.
AES-256-GCM uses the packed zero-digest header as associated data; body includes the 16-byte authentication tag.
Salt is zero without password modes; nonce zero without encryption; encrypted digest zero.
Unknown flags/reserved/version and impossible lengths fail before KDF/allocation. Output follows verification.
Benchmark deterministic PUBLIC entropy is script-only; library uses fresh `secrets.token_bytes`.
Independent vectors remain [open](https://github.com/Prajwal-Pratap-Yadav/Image-Steganography-in-Python/issues/1).
