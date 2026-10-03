"""Small file-oriented CLI. Password values never appear in arguments."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .codec import capacity, embed, extract
from .errors import StegoError
from .header import MAX_PAYLOAD
from .imageio import load_png, read_limited, save_png, write_new


def password_file(path: Path | None) -> str | None:
    if path is None:
        return None
    raw = read_limited(path, 1026)
    if raw.endswith(b"\r\n"):
        raw = raw[:-2]
    elif raw.endswith(b"\n"):
        raw = raw[:-1]
    if b"\n" in raw or b"\r" in raw:
        raise StegoError("Password file must contain a single line")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StegoError("Password file must be UTF-8") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stegolab", description="Lossless PNG payload experiments"
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    cap = commands.add_parser("capacity")
    cap.add_argument("image", type=Path)
    cap.add_argument("--depth", type=int, choices=(1, 2, 4), default=1)
    cap.add_argument("--encrypted", action="store_true")
    enc = commands.add_parser("embed")
    enc.add_argument("image", type=Path)
    enc.add_argument("payload", type=Path)
    enc.add_argument("output", type=Path)
    enc.add_argument("--depth", type=int, choices=(1, 2, 4), default=1)
    enc.add_argument("--encrypt", action="store_true")
    enc.add_argument("--keyed", action="store_true")
    enc.add_argument("--password-file", type=Path)
    dec = commands.add_parser("extract")
    dec.add_argument("image", type=Path)
    dec.add_argument("output", type=Path)
    dec.add_argument("--password-file", type=Path)
    analyze = commands.add_parser("analyze")
    analyze.add_argument("image", type=Path)
    analyze.add_argument("--cover", type=Path)
    args = parser.parse_args(argv)
    try:
        image = load_png(args.image)
        if args.command == "capacity":
            result: dict[str, object] = {
                "capacity_bytes": capacity(image, args.depth, args.encrypted)
            }
        elif args.command == "embed":
            payload = read_limited(args.payload, MAX_PAYLOAD)
            out = embed(
                image,
                payload,
                args.depth,
                password=password_file(args.password_file),
                encrypted=args.encrypt,
                keyed=args.keyed,
            )
            save_png(args.output, out)
            result = {"output": str(args.output), "payload_bytes": len(payload)}
        elif args.command == "extract":
            payload = extract(image, password=password_file(args.password_file))
            write_new(args.output, payload)
            result = {"output": str(args.output), "payload_bytes": len(payload)}
        else:
            from .analysis import analyze_image, distortion

            result = analyze_image(image)
            if args.cover:
                result["distortion"] = distortion(load_png(args.cover), image)
        print(json.dumps(result, allow_nan=False))
        return 0
    except (StegoError, OSError) as exc:
        print(f"stegolab: {exc}", file=sys.stderr)
        return 2
