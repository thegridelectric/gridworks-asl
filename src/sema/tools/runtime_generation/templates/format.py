# runtime_generation/format_templates.py

FORMAT_TEMPLATES = {
    "uuid4.str": {
        "class_name": "UUID4Str",
        "imports": ["import uuid"],
        "methods": """
def is_uuid4_str(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: uuid4.str must be a string.")

    if not UUID4_STR_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails uuid4.str format.")

    try:
        u = uuid.UUID(v)
    except Exception as e:
        raise ValueError(f"Invalid UUID4: {v}  <{e}>") from e
    if u.version != 4:
        raise ValueError(
            f"{v} is valid uid, but of version {u.version}. Fails UuidCanonicalTextual"
        )
    return str(u)
""",
        "annotated_type": """
UUID4Str = Annotated[
    str,
    BeforeValidator(is_uuid4_str),
]
""",
    },

    "left.right.dot": {
        "class_name": "LeftRightDot",
        "pattern": r"^[a-z][a-z0-9]*(?:\.[a-z0-9]+)*$",
        "methods": """
def is_left_right_dot(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: LeftRightDot must be a string.")

    if not LEFT_RIGHT_DOT_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails LeftRightDot format.")

    return v
""",
        "annotated_type": """
LeftRightDot = Annotated[
    str,
    BeforeValidator(is_left_right_dot),
]
""",
    },

    "spaceheat.name": {
        "class_name": "SpaceheatName",
        "pattern": r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$",
        "methods": """
def is_spaceheat_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: SpaceheatName must be a string.")

    if len(v) > 64:
        raise ValueError(f"<{v}>: SpaceheatName exceeds maximum length of 64.")

    if not SPACEHEAT_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails SpaceheatName format.")

    return v
""",
        "annotated_type": """
SpaceheatName = Annotated[
    str,
    BeforeValidator(is_spaceheat_name),
]
""",
    },

    "handle.name": {
        "class_name": "HandleName",
        "pattern": r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*$",
        "methods": """
def is_handle_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: HandleName must be a string.")

    if not HANDLE_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails HandleName format.")

    return v
""",
        "annotated_type": """
HandleName = Annotated[
    str,
    BeforeValidator(is_handle_name),
]
""",
    },

    "hex.char": {
        "class_name": "HexChar",
        "pattern": r"^[0-9a-fA-F]$",
        "methods": """
def is_hex_char(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: hex.char must be a string.")

    if not HEX_CHAR_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails hex.char format.")

    return v
""",
        "annotated_type": """
HexChar = Annotated[
    str,
    BeforeValidator(is_hex_char),
]
""",
    },

    "market.slot.name": {
        "class_name": "MarketSlotName",
        "pattern": r"^[erd]\.[a-z0-9]+(?:\.[a-z0-9]+)*(?:\.[a-z0-9]+)+\.[0-9]{10}$",
        "methods": """
def is_market_name(v: str) -> str:
    market_type_name_enum = _market_type_name_enum()
    try:
        x = v.split(".")
    except AttributeError as e:
        raise ValueError(f"{v} failed to split on '.'") from e
    if len(x) < 3:
        raise ValueError("MarketNames need at least 3 words")
    if x[0] not in {"e", "r", "d"}:
        raise ValueError(
            f"{v} first word must be e,r or d (energy, regulation, distribution)"
        )
    if x[1] not in market_type_name_enum.values():
        raise ValueError(f"{v} not recognized MarketType")
    g_node_alias = ".".join(x[2:])
    is_left_right_dot(g_node_alias)
    return v


def _market_type_name_enum():
    from sema.runtime.enums import MarketTypeName  # noqa: PLC0415

    return MarketTypeName


def _market_minutes() -> dict:
    market_type_name_enum = _market_type_name_enum()
    return {
        market_type_name_enum.da60: 60,
        market_type_name_enum.rt15gate5: 15,
        market_type_name_enum.rt30gate5: 30,
        market_type_name_enum.rt5gate5: 5,
        market_type_name_enum.rt60gate30: 60,
        market_type_name_enum.rt60gate30b: 60,
        market_type_name_enum.rt60gate5: 60,
    }


def is_market_slot_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: market.slot.name must be a string.")

    if not MARKET_SLOT_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails market.slot.name format.")

    try:
        x = v.split(".")
    except AttributeError as e:
        raise ValueError(f"{v} failed to split on '.'") from e
    slot_start = x[-1]
    if len(slot_start) != 10:
        raise ValueError(f"slot start {slot_start} not of length 10")
    try:
        slot_start = int(slot_start)
    except ValueError as e:
        raise ValueError(f"slot start {slot_start} not an int") from e
    is_market_name(".".join(x[:-1]))
    market_type_name = _market_type_name_enum()(x[1])
    market_minutes = _market_minutes()
    if market_type_name not in market_minutes:
        raise ValueError(f"{market_type_name} not recognized MarketType")
    market_duration_minutes = market_minutes[market_type_name]
    if not slot_start % (market_duration_minutes * 60) == 0:
        raise ValueError(
            f"market_slot_start_s mod {market_duration_minutes * 60} must be 0"
        )
    return v
""",
        "annotated_type": """
MarketName = Annotated[
    str,
    BeforeValidator(is_market_name),
]

MarketSlotName = Annotated[
    str,
    BeforeValidator(is_market_slot_name),
]
""",
    },

    "non.negative.int": {
        "class_name": "NonNegativeInt",
        "imports": ["from pydantic import Field, StrictInt"],
        "methods": """
def is_non_negative_int(v: int) -> int:
    if not isinstance(v, int):
        raise TypeError("Not an int!")
    if v < 0:
        raise ValueError(f"{v} must be non-negative")
    return v
""",
        "annotated_type": """
NonNegativeInt = Annotated[
    StrictInt,
    Field(ge=0),
]
""",
    },

    "pascal.case": {
        "class_name": "PascalCase",
        "pattern": r"^[A-Z][A-Za-z0-9]*$",
        "methods": """
def is_pascal_case(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: PascalCase must be a string.")

    if not PASCAL_CASE_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails PascalCase format.")

    return v
""",
        "annotated_type": """
PascalCase = Annotated[
    str,
    BeforeValidator(is_pascal_case),
]
""",
    },

    "positive.int": {
        "class_name": "PositiveInt",
        "methods": """
def is_positive_int(v: int) -> int:
    if not isinstance(v, int) or isinstance(v, bool):
        raise TypeError("Not an int!")
    if v <= 0:
        raise ValueError(f"{v} must be positive")
    return v
""",
        "annotated_type": """
PositiveInt = Annotated[
    int,
    BeforeValidator(is_positive_int),
]
""",
    },

    "positive.float": {
        "class_name": "PositiveFloat",
        "imports": ["from pydantic import Field, StrictFloat"],
        "methods": "",
        "annotated_type": """
PositiveFloat = Annotated[
    StrictFloat,
    Field(gt=0),
]
""",
    },

    "utc.iso8601.millis": {
        "class_name": "UtcIso8601Millis",
        "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$",
        "imports": ["from datetime import UTC, datetime"],
        "methods": """
def is_utc_iso8601_millis(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: utc.iso8601.millis must be a string.")

    if not UTC_ISO8601_MILLIS_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails utc.iso8601.millis format.")

    return v
""",
        "annotated_type": """
UtcIso8601Millis = Annotated[
    str,
    BeforeValidator(is_utc_iso8601_millis),
]
""",
        "helpers": """
class UtcIso8601MillisFormat:
    @staticmethod
    def from_datetime(dt: datetime) -> UtcIso8601Millis:
        if not isinstance(dt, datetime):
            raise TypeError(f"{dt} must be a datetime")

        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("datetime must be timezone-aware")

        dt_utc = dt.astimezone(UTC)
        millis = dt_utc.microsecond // 1000
        dt_utc = dt_utc.replace(microsecond=millis * 1000)
        s = dt_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")

        return is_utc_iso8601_millis(s)
""",
    },

    "utc.iso8601.seconds": {
        "class_name": "UtcIso8601Seconds",
        "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        "imports": ["from datetime import UTC, datetime"],
        "methods": """
def is_utc_iso8601_seconds(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: utc.iso8601.seconds must be a string.")

    if not UTC_ISO8601_SECONDS_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails utc.iso8601.seconds format.")

    return v
""",
        "annotated_type": """
UtcIso8601Seconds = Annotated[
    str,
    BeforeValidator(is_utc_iso8601_seconds),
]
""",
        "helpers": """
class UtcIso8601SecondsFormat:
    @staticmethod
    def from_datetime(dt: datetime) -> UtcIso8601Seconds:
        if not isinstance(dt, datetime):
            raise TypeError(f"{dt} must be a datetime")

        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")

        dt_utc = dt.astimezone(UTC)
        dt_utc = dt_utc.replace(microsecond=0)
        s = dt_utc.isoformat().replace("+00:00", "Z")

        return is_utc_iso8601_seconds(s)
""",
    },

    "utc.milliseconds": {
        "class_name": "UTCMilliseconds",
        "imports": ["from datetime import UTC, datetime"],
        "methods": """
def is_utc_milliseconds(v: int) -> int:
    if not isinstance(v, int):
        raise TypeError("Not an int!")
    start_date = datetime(2000, 1, 1, tzinfo=UTC)
    end_date = datetime(3000, 1, 1, tzinfo=UTC)

    start_timestamp_ms = int(start_date.timestamp() * 1000)
    end_timestamp_ms = int(end_date.timestamp() * 1000)

    if v < start_timestamp_ms:
        raise ValueError(f"{v} must be after Jan 1 2000")
    if v > end_timestamp_ms:
        raise ValueError(f"{v} must be before Jan 1 3000")
    return v
""",
        "annotated_type": """
UTCMilliseconds = Annotated[
    int,
    BeforeValidator(is_utc_milliseconds),
]
""",
    },

    "utc.seconds": {
        "class_name": "UTCSeconds",
        "imports": ["from datetime import UTC, datetime"],
        "methods": """
def is_utc_seconds(v: int) -> int:
    if not isinstance(v, int):
        raise ValueError("Not an int!")
    start_date = datetime(2000, 1, 1, tzinfo=UTC)
    end_date = datetime(3000, 1, 1, tzinfo=UTC)

    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    if v < start_timestamp:
        raise ValueError(f"{v}: Fails UTCSeconds format! Must be after Jan 1 2000")
    if v > end_timestamp:
        raise ValueError(f"{v}: Fails UTCSeconds format! Must be before Jan 1 3000")
    return v
""",
        "annotated_type": """
UTCSeconds = Annotated[
    int,
    BeforeValidator(is_utc_seconds),
]
""",
    },
}
