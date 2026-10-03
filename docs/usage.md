# File-oriented usage

After `make setup`, `.venv/bin/stegolab` is installed.

```sh
.venv/bin/stegolab capacity examples/cover.png --depth 2
.venv/bin/stegolab embed examples/cover.png examples/message.txt /tmp/public-stego.png --depth 2
.venv/bin/stegolab extract /tmp/public-stego.png /tmp/public-decoded.txt
.venv/bin/stegolab analyze /tmp/public-stego.png --cover examples/cover.png
```

Choose unused paths; existing files are refused. No conversion or shell image viewer runs.
To encrypt, create a private single-line UTF-8 password file outside Git, restrict its permissions, and add
`--encrypt --keyed --password-file /path/to/private-password` to embed. Extract with the same password-file argument.
Never put password values in arguments, examples or Git. Length validation makes no password strength promise.
One trailing line ending is removed; multiline/invalid UTF-8 files fail. Keyed plaintext authenticates without encryption.
Binary and empty payloads are supported; [format constants](../reports/format.json) define bounds and overhead.
Verification completes before extracted output is written. Supported setup is Linux/macOS; Windows remains roadmap work.
