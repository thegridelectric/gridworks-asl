<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl" xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xsl:output method="xml" indent="yes" />
    <xsl:param name="root" />
    <xsl:param name="codee-root" />
    <xsl:include href="../CommonXsltTemplates.xslt"/>
    <xsl:param name="exclude-collections" select="'false'" />
    <xsl:param name="relationship-suffix" select="''" />
    <xsl:variable name="airtable" select="/" />
    <xsl:variable name="squot">'</xsl:variable>
    <xsl:variable name="init-space">             </xsl:variable>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <FileSet>

            <FileSetFile>
                    <xsl:element name="RelativePath"><xsl:text>../../../../src/gwproto/property_format.py</xsl:text></xsl:element>

                <OverwriteMode>Always</OverwriteMode>
                <xsl:element name="FileContents">

<xsl:text>
# ruff: noqa: ANN401
import re
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Callable, List

import pydantic
from pydantic import BeforeValidator, Field

UTC_2000_01_01_TIMESTAMP = datetime(2000, 1, 1, tzinfo=timezone.utc).timestamp()
UTC_3000_01_01_TIMESTAMP = datetime(3000, 1, 1, tzinfo=timezone.utc).timestamp()


def predicate_validator(
    field_name: str,
    predicate: Callable[[Any], bool],
    error_format: str = "",
    **kwargs: dict[str, Any],
) -> classmethod:
    """
    Produce a pydantic validator from a function returning a bool.

    Example:

        from typing import Any
        from pydantic import BaseModel, ValidationError
        from gwproto.property_format import predicate_validator

        def is_truthy(v: Any) -> bool:
            return bool(v)

        class Foo(BaseModel):
            an_int: int

            _validate_an_int = predicate_validator("an_int", is_truthy)

        print(Foo(an_int=1))

        try:
            print(Foo(an_int=0))
        except ValidationError as e:
            print(e)

    Args:
        field_name: the name of the field to validate.
        predicate: the validation function. A truthy return value indicates success.
        error_format: Optional format string for use in exception raised by validation failure. Takes one parameter, 'v'.
        **kwargs: Passed to pydantic.validator()

    Returns:
        The passed in object v.
    """

    def _validator(v: Any) -> Any:
        if not predicate(v):
            if error_format:
                err_str = error_format.format(value=v)
            else:
                err_str = f"Failure of predicate on [{v}] with predicate {predicate}"
            raise ValueError(err_str)
        return v

    return pydantic.field_validator(field_name, **kwargs)(_validator)


def check_is_log_style_date_with_millis(v: str) -> None:
    """Checks LogStyleDateWithMillis format

    LogStyleDateWithMillis format:  YYYY-MM-DDTHH:mm:ss.SSS

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not LogStyleDateWithMillis format.
        In particular the milliseconds must have exactly 3 digits.
    """
    correct_millisecond_part_length = 3
    try:
        datetime.fromisoformat(v)
    except ValueError as e:
        raise ValueError(f"{v} is not in LogStyleDateWithMillis format") from e
    # The python fromisoformat allows for either 3 digits (milli) or 6 (micro)
    # after the final period. Make sure its 3
    milliseconds_part = v.split(".")[1]
    if len(milliseconds_part) != correct_millisecond_part_length:
        raise ValueError(
            f"{v} is not in LogStyleDateWithMillis format."
            " Milliseconds must have exactly 3 digits"
        )


def is_handle_name(v: str) -> None:
    """
    HandleName format: words separated by periods, where the worlds are lowercase
    alphanumeric plus hyphens
    """
    try:
        x = v.split(".")
    except Exception as e:
        raise ValueError(f"Failed to seperate &lt;{v}> into words with split'.'") from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word of &lt;{v}> must start with alphabet char."
        )
    for word in x:
        for char in word:
            if not (char.isalnum() or char == "-"):
                raise ValueError(
                    f"words of &lt;{v}> split by by '.' must be alphanumeric or hyphen."
                )
    if not v.islower():
        raise ValueError(f" &lt;{v}> must be lowercase.")
    return v


def is_hex_char(v: str) -> str:
    """Checks HexChar format

    HexChar format: single-char string in '0123456789abcdefABCDEF'

    Args:
        v (str): the candidate

    Raises:
        ValueError: if v is not HexChar format
    """
    if not isinstance(v, str):
        raise ValueError(f"&lt;{v}> must be string. Got type &lt;{type(v)}")  # noqa: TRY004
    if len(v) > 1:
        raise ValueError(f"&lt;{v}> must be a hex char, but not of len 1")
    if v not in "0123456789abcdefABCDEF":
        raise ValueError(f"&lt;{v}> must be one of '0123456789abcdefABCDEF'")
    return v


def is_int(v: int) -> int:
    if not isinstance(v, int):
        raise TypeError("Not an integer!")
    return v


def is_left_right_dot(candidate: str) -> str:
    """Lowercase AlphanumericStrings separated by dots (i.e. periods), with most
    significant word to the left.  I.e. `d1.ne` is the child of `d1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter


    Raises:
        ValueError: if candidate is not of lrd format (e.g. d1.iso.me.apple)
    """
    try:
        x: List[str] = candidate.split(".")
    except Exception as e:
        raise ValueError("Failed to seperate into words with split'.'") from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word must start with alphabet char. Got '{first_word}'"
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(
                f"words seperated by dots must be alphanumeric. Got '{word}'"
            )
    if not candidate.islower():
        raise ValueError(f"alias must be lowercase. Got '{candidate}'")
    return candidate



MAC_REGEX = re.compile("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$")


def has_mac_address_format(mac_str: str) -> bool:
    return bool(MAC_REGEX.match(mac_str.lower()))


def is_spaceheat_name(v: str) -> str:
    """
    SpaceheatName format: Lowercase alphanumeric words separated by hypens
    """
    try:
        x = v.split("-")
    except Exception as e:
        raise ValueError(
            f"&lt;{v}>: Fails SpaceheatName format! Failed to seperate into words with split'-'"
        ) from e
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"&lt;{v}>: Fails SpaceheatName format! Most significant word  must start with alphabet char."
        )
    for word in x:
        if not word.isalnum():
            raise ValueError(
                f"&lt;{v}>: Fails SpaceheatName format! words of split by by '-' must be alphanumeric."
            )
    if not v.islower():
        raise ValueError(
            f"&lt;{v}>: Fails SpaceheatName format! All characters of  must be lowercase."
        )
    return v


def is_uuid4_str(v: str) -> str:
    v = str(v)
    try:
        u = uuid.UUID(v)
    except Exception as e:
        raise ValueError(f"Invalid UUID4: &lt;{v}  &lt;{e}>") from e
    if u.version != 4:
        raise ValueError(f"{v} is valid uid, but of version {u.version}, not 4")
    return str(u)


def is_world_instance_name_format(candidate: str) -> bool:
    try:
        words = candidate.split("__")
    except:  # noqa
        return False
    if len(words) != 2:
        return False
    try:
        int(words[1])
    except:  # noqa
        return False
    try:
        root_g_node_alias_words = words[0].split(".")
    except:  # noqa
        return False
    return not len(root_g_node_alias_words) > 1


def check_is_ads1115_i2c_address(v: int) -> None:
    """
    Ads1115I2cAddress: ToLower(v) in  [0x48, 0x49, 0x4a, 0x4b].

    One of the 4 allowable I2C addresses for Texas Instrument Ads1115 chips.

    Raises:
        ValueError: if not Ads1115I2cAddress format
    """
    if v not in [0x48, 0x49, 0x4a, 0x4b]:
        raise ValueError(f"Not Ads1115I2cAddress: &lt;{v}>")


def check_is_near5(v: str) -> None:
    """
    4.5  &lt;= v  &lt;= 5.5
    """
    min_pi_voltage = 4.5
    max_pi_voltage = 5.5
    if v  &lt; min_pi_voltage or v > max_pi_voltage:
        raise ValueError(f"&lt;{v}> is not between 4.5 and 5.5, not Near5")</xsl:text>


def is_bit(candidate: int) -> int:
    if candidate not in (0, 1):
        raise ValueError(f"Candidate must be 0 or 1, Got {candidate}")
    return candidate


Bit = Annotated[int, BeforeValidator(is_bit)]
HandleName = Annotated[str, BeforeValidator(is_handle_name)]
HexChar = Annotated[str, BeforeValidator(is_hex_char)]
LeftRightDotStr = Annotated[str, BeforeValidator(is_left_right_dot)]
SpaceheatName = Annotated[str, BeforeValidator(is_spaceheat_name)]
ReallyAnInt = Annotated[int, BeforeValidator(is_int)]
UUID4Str = Annotated[str, BeforeValidator(is_uuid4_str)]
UTCSeconds = Annotated[
    int, Field(ge=UTC_2000_01_01_TIMESTAMP, le=UTC_3000_01_01_TIMESTAMP)
]
UTCMilliseconds = Annotated[
    int, Field(ge=UTC_2000_01_01_TIMESTAMP * 1000, le=UTC_3000_01_01_TIMESTAMP * 1000)
]


<!-- Add newline at EOF for git and pre-commit-->
<xsl:text>&#10;</xsl:text>

                </xsl:element>
            </FileSetFile>


        </FileSet>
    </xsl:template>


</xsl:stylesheet>
