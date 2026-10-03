# ADR: library authentication and independent keys

Accepted: cryptography AES-GCM/scrypt and separate encryption, ordering and keyed-plaintext MAC keys.
The header is associated data; keyed plaintext also authenticates empty/constant bodies that could otherwise appear to
succeed under any ordering. Partial Fisher–Yates/ChaCha20 ordering is versioned independently of NumPy permutations.
Cost: fixed KDF work/memory. Password guessing and steganalysis remain limits.
Primary docs: [AEAD](https://cryptography.io/en/50.0.2/hazmat/primitives/aead/),
[scrypt](https://cryptography.io/en/50.0.2/hazmat/primitives/key-derivation-functions/),
[stream cipher](https://cryptography.io/en/50.0.2/hazmat/primitives/symmetric-encryption/).
