# ADR: lossless framing

Accepted: RGB/RGBA PNG with visible fixed header and binary body. Reject lossy/ambiguous pixel modes rather than convert.
Length framing supports arbitrary bytes without terminators. Cost: overhead and recognizable signature. Preserve alpha.
Original script is byte unchanged with characterization; compatibility with its unframed JPEG is not promised.
