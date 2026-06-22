import argparse
import sys

from sema.interfaces.cli import reverse, runtime, snapshot, validate


def _run_info(_: argparse.Namespace) -> None:
    print("Sema CLI")
    print("Interface: textual")
    print("Subcommands: reverse, runtime, snapshot, validate, info")
    print("Use `uv run sema reverse --help` for reverse dependency examples.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sema")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reverse.add_parser(subparsers)
    runtime.add_parser(subparsers)
    snapshot.add_parser(subparsers)
    validate.add_parser(subparsers)

    info_parser = subparsers.add_parser("info")
    info_parser.set_defaults(handler=_run_info)

    args = parser.parse_args()
    try:
        args.handler(args)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
