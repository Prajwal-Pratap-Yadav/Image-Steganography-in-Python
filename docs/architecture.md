# Architecture

CLI owns file arguments and JSON/errors. imageio reads one bounded byte snapshot, validates PNG headers before decompression
and writes new images without metadata. codec frames binary payloads; header rejects unsupported or impossible formats.
crypto separates encryption, ordering and MAC keys. analysis computes explicit comparisons and exploratory statistics.

Extraction needs only saved PNG/password, not the cover, known length or previous memory. Bounds precede KDF, authentication
precedes writes, alpha never participates. README has the flow diagram; [format](format.md) defines framing and
[security](security.md) defines limits.
