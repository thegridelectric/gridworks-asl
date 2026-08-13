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

    "hh.mm": {
        "class_name": "HhMm",
        "pattern": r"^([01][0-9]|2[0-3]):[0-5][0-9]$",
        "methods": """
def is_hh_mm(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: hh.mm must be a string.")

    if not HH_MM_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails hh.mm format.")

    return v
""",
        "annotated_type": """
HhMm = Annotated[
    str,
    BeforeValidator(is_hh_mm),
]
""",
    },

    "market.slot.name": {
        "class_name": "MarketSlotName",
        # Self-contained leaf (no enum, no other-format calls):
        #   [erd] . <product: spaceheat.name shape> . <maker alias: left.right.dot shape> . <10-digit slot start>
        # The product segment is constrained to the single-token spaceheat.name
        # shape (lowercase, internal hyphens, no dots). The slot start MUST be
        # divisible by 300 — every market slot starts on a 5-minute grid (a
        # GridWorks ecosystem invariant; arithmetic, so enforced in the
        # validator, not the pattern). Whether the token is a real product, and
        # whether the start aligns to that product's specific slot duration,
        # remain the receiving market maker's concern (decoded opt-in via that
        # maker's product-name enum).
        "pattern": r"^[erd]\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*\.[a-z][a-z0-9]*(?:\.[a-z0-9]+)*\.[0-9]{10}$",
        "methods": """
def is_market_slot_name(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: market.slot.name must be a string.")

    if not MARKET_SLOT_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails market.slot.name format.")

    slot_start = int(v.rsplit(".", 1)[1])
    if slot_start % 300 != 0:
        raise ValueError(
            f"<{v}>: market.slot.name slot start {slot_start} must be divisible "
            "by 300 (every market slot starts on a 5-minute grid)."
        )

    return v
""",
        "annotated_type": """
MarketSlotName = Annotated[
    str,
    BeforeValidator(is_market_slot_name),
]
""",
    },

    "mac.address": {
        "class_name": "MacAddress",
        "pattern": r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$",
        "methods": """
def is_mac_address(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: mac.address must be a string.")

    if not MAC_ADDRESS_PATTERN.fullmatch(v):
        raise ValueError(
            f"<{v}>: Fails mac.address format (six lowercase hex octet pairs, colon-separated)."
        )

    return v
""",
        "annotated_type": """
MacAddress = Annotated[
    str,
    BeforeValidator(is_mac_address),
]
""",
    },

    "non.empty.string": {
        "class_name": "NonEmptyString",
        "imports": ["from pydantic import Field"],
        "methods": "",
        "annotated_type": """
NonEmptyString = Annotated[
    str,
    Field(min_length=1),
]
""",
    },

    "positive.int.as.str": {
        "class_name": "PositiveIntAsStr",
        "pattern": r"^[1-9][0-9]*$",
        "methods": """
def is_positive_int_as_str(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: positive.int.as.str must be a string.")
    if not POSITIVE_INT_AS_STR_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails positive.int.as.str format.")
    return v
""",
        "annotated_type": """
PositiveIntAsStr = Annotated[
    str,
    BeforeValidator(is_positive_int_as_str),
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
