# StegoLab: review guide

Trace a versioned image-payload format through capacity checks, optional encryption, malformed-input handling, and reproducible measurements.

## Follow the implementation

| Start here | File | What to inspect |
| --- | --- | --- |
| Binary header | [src/stegolab/header.py](../src/stegolab/header.py) | Version, lengths, and format boundaries. |
| Codec | [src/stegolab/codec.py](../src/stegolab/codec.py) | Capacity accounting and pixel embedding. |
| Cryptography boundary | [src/stegolab/crypto.py](../src/stegolab/crypto.py) | Optional encryption and key handling. |
| Malformed-input tests | [tests/test_malformed.py](../tests/test_malformed.py) | Truncation and invalid metadata rejection. |
| Codec tests | [tests/test_codec.py](../tests/test_codec.py) | Round trips and capacity edge cases. |
| Security model | [docs/security.md](../docs/security.md) | What confidentiality and concealment claims the format supports. |

## Run the checks

Run from the repository root after the setup described in the [README](../README.md). Review fixtures and recorded evidence before starting any full experiment.

```bash
make setup-dev
make test docs
make reproduce
```

## Interpret the evidence

Version 0.1.2 and its release remain immutable. A visible header and keyed ordering are not a guarantee of undetectable communication. Recorded synthetic-image steganalysis does not establish performance on natural photographs or against an adaptive adversary.

The linked reports retain their original experiment dates and protocols. A new passing CI run verifies its named checks; it does not silently refresh historical measurements.

## Discuss the design

- Which bytes must be validated before allocating or decrypting a payload?
- How would a natural-image corpus change the interpretation of the current measurements?
