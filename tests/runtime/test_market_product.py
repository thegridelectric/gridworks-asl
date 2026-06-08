"""market.product — the open, maker-agnostic product type (untangle Unit 3).

market.product does not pin a specific product-name enum: ProductNameEnum names
whichever maker's *.market.product.name vocabulary Name is drawn from, and Name
is a bare token (not $ref'd to that enum). Two consequences are tested here:
the type decodes for any maker's enum name, and a snapshot seeding market.product
alone pulls in NO product enum (decode is opt-in).
"""

from pathlib import Path

import yaml

from sema.runtime.codec import default_codec
from sema.runtime.types.market_product import MarketProduct


REPO_ROOT = Path(__file__).resolve().parents[2]


def _instance(product_name_enum: str, name: str) -> dict:
    return {
        "TypeName": "market.product",
        "Version": "000",
        "MarketProductId": "97eba574-bd20-45b5-bf82-9ba2f492d8f3",
        "ProductNameEnum": product_name_enum,
        "Name": name,
    }


def test_market_product_decode_is_maker_agnostic() -> None:
    # A non-GridWorks maker's vocabulary decodes just as well; Name is a bare
    # token, not validated against any enum.
    decoded = default_codec.from_dict(_instance("acme.market.product.name", "wholesale7"))
    assert isinstance(decoded, MarketProduct)
    assert decoded.product_name_enum == "acme.market.product.name"
    assert decoded.name == "wholesale7"

    # GridWorks's own vocabulary is just one valid value of ProductNameEnum.
    gw = default_codec.from_dict(_instance("gw.market.product.name", "rt60gate5"))
    assert gw.product_name_enum == "gw.market.product.name"


def test_market_product_seeded_alone_pulls_no_enum() -> None:
    closure = yaml.safe_load((REPO_ROOT / "indexes" / "dependency_closure.yaml").read_text())
    entry = closure["types"]["market.product"]["000"]
    # Open model: no product enum is dragged in by the type itself.
    assert entry["enums"] == []
    # It depends only on the two formats it $refs.
    assert set(entry["formats"]) == {"left.right.dot", "uuid4.str"}
