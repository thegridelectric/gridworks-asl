import argparse
import sys

from sema.runtime.validate import validate


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate",
        add_help=False,
        help="Validate a serialized payload against the Sema vocabulary",
        description=(
            "Decode a JSON payload (a file, or stdin) through the Sema runtime — a\n"
            "clean decode means it conforms to its declared type's schema (fields,\n"
            "property formats, axioms, version). Sema is the source of truth, so this\n"
            "validates against the canonical runtime, not a codegen'd copy.\n\n"
            "Exit 0 if valid, 2 if not."
        ),
        epilog=(
            "Examples:\n"
            "  uv run sema validate payload.json\n"
            "  cat payload.json | uv run sema validate\n"
            "  uv run sema validate --type i2c.result payload.json"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-h", "--help", action="help", help=argparse.SUPPRESS)
    parser.add_argument("file", nargs="?", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--type", dest="expected_type", default=None, help=argparse.SUPPRESS)
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace) -> None:
    text = open(args.file).read() if args.file else sys.stdin.read()
    result = validate(text, expected_type=args.expected_type)
    if result.ok:
        print(f"OK: {result.type_name} (version {result.version})")
        return
    label = result.type_name or "<unknown>"
    print(f"INVALID ({label}): {result.error}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    parser = argparse.ArgumentParser(prog="sema validate")
    parser.add_argument("file", nargs="?", default=None)
    parser.add_argument("--type", dest="expected_type", default=None)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
