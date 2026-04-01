import argparse

from sema.runtime.reverse_query import load_reverse_index, reverse_transitive


def _set_repr(values: set[str]) -> str:
    if not values:
        return "set()"
    return "{" + ", ".join(repr(value) for value in sorted(values)) + "}"


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "reverse",
        add_help=False,
        help="Show transitive reverse dependencies for a Sema word",
        description=(
            "Return the transitive reverse dependency closure for a Sema word.\n\n"
            "If the word is a type or enum, it MUST include a version.\n"
            "If the word is a property format, it has no version."
        ),
        epilog=(
            "Examples:\n"
            "  uv run sema reverse relay.actor.config 003\n"
            "  uv run sema reverse gw1.unit 001\n"
            "  uv run sema reverse left.right.dot"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-h", "--help", action="help", help=argparse.SUPPRESS)
    parser.add_argument("name", help=argparse.SUPPRESS)
    parser.add_argument("version", nargs="?", default=None, help=argparse.SUPPRESS)
    parser.set_defaults(handler=run)


def _infer_category(name: str, version: str | None) -> str:
    reverse = load_reverse_index()

    if version is None:
        if name in reverse.get("formats", {}):
            return "format"
        raise ValueError(
            f"{name} requires a 3-digit version. "
            f"Example: `uv run sema reverse {name} 001`"
        )

    if version in reverse.get("types", {}).get(name, {}):
        return "type"
    if version in reverse.get("enums", {}).get(name, {}):
        return "enum"
    raise ValueError(
        f"Unknown versioned Sema word: {name}:{version}. "
        f"For types and enums, the version must be a 3-digit string such as `001`."
    )


def run(args: argparse.Namespace) -> None:
    category = _infer_category(args.name, args.version)

    result = reverse_transitive(
        category=category,
        name=args.name,
        version=args.version,
    )

    print(_set_repr(result))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("version", nargs="?", default=None)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
