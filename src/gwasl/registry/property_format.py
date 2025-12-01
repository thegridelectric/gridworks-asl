import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BeforeValidator

from gwasl.registry.enums import MarketTypeName

def is_algo_address(v: str) -> str:
    """
    AlgoAddressStringFormat format: The public key of a private/public Ed25519
    key pair, transformed into an  Algorand address, by adding a 4-byte checksum
    to the end of the public key and then encoding in base32.

    Raises:
        ValueError: if not AlgoAddressStringFormat format
    """
    return v
    # import algosdk
    # at = algosdk.abi.AddressType()
    # try:
    #     at.decode(at.encode(v))
    # except Exception as e:
    #     raise ValueError(f"Not AlgoAddressStringFormat: {e}") from e
    # return v


def is_hex_char(v: str) -> str:
    """Checks HexChar format

    HexChar format: single-char string in '0123456789abcdefABCDEF'

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not HexChar format
    """
    if not isinstance(v, str):
        raise ValueError(f"<{v}> must be string. Got type <{type(v)}")  # noqa: TRY004
    if len(v) > 1:
        raise ValueError(f"<{v}> must be a hex char, but not of len 1")
    if v not in "0123456789abcdefABCDEF":
        raise ValueError(f"<{v}> must be one of '0123456789abcdefABCDEF'")
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
    HandleName format: words separated by periods, where the worlds are lowercase
    alphanumeric plus hyphens
    """
    try:
        x = v.split(".")
    except Exception as e:
        raise ValueError(f"Failed to seperate <{v}> into words with split'.'") from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word of <{v}> must start with alphabet char."
        )
    for word in x:
        for char in word:
            if not (char.isalnum() or char == "-"):
                raise ValueError(
                    f"words of <{v}> split by by '.' must be alphanumeric or hyphen."
                )
    if not v.islower():
        raise ValueError(f" <{v}> must be lowercase.")
    return v


def is_left_right_dot(v: str) -> str:
    """
    LeftRightDot format: Lowercase alphanumeric words separated by periods, with
    the most significant word (on the left) starting with an alphabet character.
    """
    try:
        x = v.split(".")
    except Exception as e:
        raise ValueError(
            f"<{v}>: Fails LeftRightDot format! Failed to seperate into words with split'.'"
        ) from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"<{v}>: Fails LeftRightDot format! Most significant word of  must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(
                f"<{v}>: Fails LeftRightDot format! words split by by '.' must be alphanumeric."
            )
    if not v.islower():
        raise ValueError(
            f"<{v}>: Fails LeftRightDot format! All characters must be lowercase."
        )
    return v


def is_spaceheat_name(v: str) -> str:
    """
    SpaceheatName format: Lowercase alphanumeric words separated by hypens
    """
    try:
        x = v.split("-")
    except Exception as e:
        raise ValueError(
            f"<{v}>: Fails SpaceheatName format! Failed to seperate into words with split'-'"
        ) from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"<{v}>: Fails SpaceheatName format! Most significant word  must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(
                f"<{v}>: Fails SpaceheatName format! words of split by by '-' must be alphanumeric."
            )
    if not v.islower():
        raise ValueError(
            f"<{v}>: Fails SpaceheatName format! All characters of  must be lowercase."
        )
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
    if x[1] not in MarketTypeName.values():
        raise ValueError(f"{v} not recognized MarketType")
    g_node_alias = ".".join(x[2:])
    is_left_right_dot(g_node_alias)
    return v


MarketMinutes: dict[MarketTypeName, int] = {
    MarketTypeName.da60: 60,
    MarketTypeName.rt15gate5: 15,
    MarketTypeName.rt30gate5: 30,
    MarketTypeName.rt5gate5: 5,
    MarketTypeName.rt60gate30: 60,
    MarketTypeName.rt60gate30b: 60,
    MarketTypeName.rt60gate5: 60,
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
    market_type_name = MarketTypeName(x[1])
    market_duration_minutes = MarketMinutes[market_type_name]
    if not slot_start % (market_duration_minutes * 60) == 0:
        raise ValueError(
            f"market_slot_start_s mod {market_duration_minutes * 60} must be 0"
        )
    return v


HandleName = Annotated[str, BeforeValidator(is_handle_name)]
HexChar = Annotated[str, BeforeValidator(is_hex_char)]
LeftRightDot = Annotated[str, BeforeValidator(is_left_right_dot)]
MarketName = Annotated[str, BeforeValidator(is_market_name)]
MarketSlotName = Annotated[str, BeforeValidator(is_market_slot_name)]
SpaceheatName = Annotated[str, BeforeValidator(is_spaceheat_name)]
UTCMilliseconds = Annotated[int, BeforeValidator(is_utc_milliseconds)]
UTCSeconds = Annotated[int, BeforeValidator(is_utc_seconds)]
UUID4Str = Annotated[str, BeforeValidator(is_uuid4_str)]
AlgoAddress = Annotated[str, BeforeValidator(is_algo_address)]
