import uuid
import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BeforeValidator, Field, StrictInt

_LEFT_RIGHT_DOT_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:\.[a-z0-9]+)*$"
)

_SPACEHEAT_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"
)


_HANDLE_PATTERN = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*$"
)


UTC_SECONDS_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
)

UTC_MILLIS_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$"
)


def is_utc_iso8601_seconds(v: str) -> str:
    """
    utc.iso8601.seconds format:
    UTC timestamp in ISO 8601 format with second precision (no fractional seconds)
    and a 'Z' suffix.
    Example: 2025-02-26T00:00:00Z
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: utc.iso8601.seconds must be a string.")

    if not UTC_SECONDS_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails utc.iso8601.seconds format.")

    return v


def is_utc_iso8601_millis(v: str) -> str:
    """
    utc.iso8601.millis format:
    UTC timestamp in ISO 8601 format with exactly three digits of fractional
    seconds and a 'Z' suffix.
    Example: 2025-02-26T00:00:00.000Z
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: utc.iso8601.millis must be a string.")

    if not UTC_MILLIS_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails utc.iso8601.millis format.")

    return v


def is_utc_milliseconds(v: int) -> int:
    """
    UTCMilliseconds format: unix milliseconds between Jan 1 2000 and Jan 1 3000
    """
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


def is_utc_seconds(v: int) -> int:
    """
    UTCSeconds format: unix seconds between Jan 1 2000 and Jan 1 3000
    """
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


def is_handle_name(v: str) -> str:
    """
    HandleName format:
    Dot-separated hierarchical identifier composed of lowercase
    alphanumeric segments with optional internal hyphen-separated words.

    Rules:
      - Each segment must start with a lowercase letter
      - Hyphens may appear only between alphanumeric characters
      - No trailing or leading hyphens in any segment
      - No empty segments
      - Entire string must be lowercase
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: HandleName must be a string.")

    if not _HANDLE_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails HandleName format.")

    return v


def is_left_right_dot(v: str) -> str:
    """
    Validate the LeftRightDot format.

    Rules:
      - Must be a string
      - Dot-separated segments
      - First segment must start with a lowercase letter
      - All segments must be lowercase alphanumeric
      - No empty segments
      - No leading or trailing dots
      - No hyphens or underscores
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: LeftRightDot must be a string.")

    if not _LEFT_RIGHT_DOT_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails LeftRightDot format.")

    return v


def is_spaceheat_name(v: str) -> str:
    """
    Validate the SpaceheatName format.

    Rules:
      - Must be a string
      - Single segment (no dots)
      - Must start with a lowercase alphabetic character
      - May contain lowercase alphanumeric characters
      - Hyphens allowed only between alphanumeric characters
      - No leading or trailing hyphens
      - No consecutive hyphens
      - Entire string must be lowercase
      - Maximum length 64 characters
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}>: SpaceheatName must be a string.")
    
    if len(v) > 64:
        raise ValueError(f"<{v}>: SpaceheatName exceeds maximum length of 64.")

    if not _SPACEHEAT_NAME_PATTERN.fullmatch(v):
        raise ValueError(f"<{v}>: Fails SpaceheatName format.")

    return v


def is_uuid4_str(v: str) -> str:
    """
    UuidCanonicalTextual format:  A string of hex words separated by hyphens
    of length 8-4-4-4-12.
    """
    v = str(v)
    try:
        u = uuid.UUID(v)
    except Exception as e:
        raise ValueError(f"Invalid UUID4: {v}  <{e}>") from e
    if u.version != 4:
        raise ValueError(
            f"{v} is valid uid, but of version {u.version}. Fails UuidCanonicalTextual"
        )
    return str(u)


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
    """
    MaketSlotNameLrdFormat: the format of a MarketSlotName.
      - First word must be e, r or d (energy, regulation, distribution)
      - The second word must be a MarketTypeName
      - The last word (unix time of market slot start) must
      be a 10-digit integer divisible by 300 (i.e. all MarketSlots
      start at the top of 5 minutes)
      - More strictly, the last word must be the start of a
      MarketSlot for that MarketType (i.e. divisible by 3600
      for hourly markets)
      - The middle words have LeftRightDot format (GNodeAlias
      of the MarketMaker)
    Example: e.rt60gate5.d1.isone.ver.keene.1673539200

    """
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
    market_duration_minutes = _market_minutes()[market_type_name]
    if not slot_start % (market_duration_minutes * 60) == 0:
        raise ValueError(
            f"market_slot_start_s mod {market_duration_minutes * 60} must be 0"
        )
    return v




HandleName = Annotated[str, BeforeValidator(is_handle_name)]
LeftRightDot = Annotated[str, BeforeValidator(is_left_right_dot)]
MarketName = Annotated[str, BeforeValidator(is_market_name)]
MarketSlotName = Annotated[str, BeforeValidator(is_market_slot_name)]
SpaceheatName = Annotated[str, BeforeValidator(is_spaceheat_name)]
NonNegativeInt = Annotated[StrictInt, Field(ge=0)]
PositiveInt = Annotated[StrictInt, Field(gt=0)]
UTCMilliseconds = Annotated[int, BeforeValidator(is_utc_milliseconds)]
UTCSeconds = Annotated[int, BeforeValidator(is_utc_seconds)]
UUID4Str = Annotated[str, BeforeValidator(is_uuid4_str)]
UtcIso8601Seconds = Annotated[str, BeforeValidator(is_utc_iso8601_seconds)]
UtcIso8601Millis = Annotated[str, BeforeValidator(is_utc_iso8601_millis)]



class UtcIso8601SecondsFormat:
    @staticmethod
    def from_datetime(dt: datetime) -> UtcIso8601Seconds:
        """
        Convert a timezone-aware datetime to utc.iso8601.seconds format.

        Rules enforced:
        - Must be timezone-aware
        - Converted to UTC
        - No fractional seconds
        - 'Z' suffix
        """
        if not isinstance(dt, datetime):
            raise TypeError(f"{dt} must be a datetime")

        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")

        dt_utc = dt.astimezone(UTC)

        # Strip microseconds to enforce second precision
        dt_utc = dt_utc.replace(microsecond=0)

        s = dt_utc.isoformat().replace("+00:00", "Z")

        # Optional but recommended: validate against Sema format
        return is_utc_iso8601_seconds(s)


class UtcIso8601MillisFormat:
    @staticmethod
    def from_datetime(dt: datetime) -> UtcIso8601Millis:
        """
        Convert a timezone-aware datetime to utc.iso8601.millis format.

        Rules enforced:
        - Must be timezone-aware
        - Converted to UTC
        - Exactly 3 digits of fractional seconds (milliseconds)
        - 'Z' suffix
        """
        if not isinstance(dt, datetime):
            raise TypeError(f"{dt} must be a datetime")

        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("datetime must be timezone-aware")

        dt_utc = dt.astimezone(UTC)

        # Convert microseconds → milliseconds (truncate, not round)
        millis = dt_utc.microsecond // 1000

        # Rebuild datetime with truncated microseconds
        dt_utc = dt_utc.replace(microsecond=millis * 1000)

        # Format with exactly 3 decimal places
        s = dt_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")

        return is_utc_iso8601_millis(s)