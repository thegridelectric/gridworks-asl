"""
Mock-data additions to demonstrate the Explorer's UI/UX surfaces:
  M1 — drafts (3 TypeVersions + 2 EnumVersions, each with child rows)
  M2 — Word-level retirement (1 each: Type, Enum, Format)
  M3 — deprecated non-leaf TypeVersions (20 rows from existing upgrade chains)
  M4 — published artifacts for the 3 empty Owners
  M5 — EnumUpgrades + EnumUpgradeMappings (2 chains)
  M6 — fix the 2 existing Projections' null endpoints

Idempotent: existing rows are detected by their identity tuple and skipped.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULEBOOK = ROOT / "effortless-rulebook" / "effortless-rulebook.json"

# Stamps for newly-added rows. Keep them all the same so the Activity feed has
# a clean "this batch landed today" cluster.
NOW = "2026-04-30T18:00:00Z"
RECENT_DEPRECATION = "2026-04-30T18:05:00Z"


def find_index(data, predicate):
    for i, row in enumerate(data):
        if predicate(row):
            return i
    return -1


def upsert_row(table_data, row, key_fn):
    """Append row if key_fn(row) doesn't already match an existing row."""
    target_key = key_fn(row)
    for existing in table_data:
        if key_fn(existing) == target_key:
            # Patch in any missing keys (idempotent update for status etc.)
            for k, v in row.items():
                existing.setdefault(k, v)
            return False
    table_data.append(row)
    return True


def main():
    rb = json.loads(RULEBOOK.read_text())

    # ============================================================
    # M2 — Word-level retirement: invent successor for each retirement
    # ============================================================
    # New Format `market.slot.handle` to receive `market.slot.name`'s retirement.
    upsert_row(rb["Formats"]["data"], {
        "Name": "market.slot.handle",
        "Owner": "gridworks-energy",
        "SchemaUrl": "https://schemas.electricity.works/formats/market.slot.handle",
        "Title": "Market Slot Handle",
        "Description": "Successor to market.slot.name. Adds a checksum suffix so a slot handle is self-validating without a registry lookup.",
        "ReplacedBy": None,
        "Pattern": "^[a-z][a-z0-9.]*\\.[a-f0-9]{4}$",
        "MinLength": 6,
        "MaxLength": 80,
        "JsonSchemaFormat": None,
        "Created": NOW,
        "RawJson": None,
    }, key_fn=lambda r: r["Name"])

    # New Type `gridworks.heartbeat` to receive `gridworks.ping`'s retirement.
    upsert_row(rb["Types"]["data"], {
        "Name": "gridworks.heartbeat",
        "Owner": "smoothstone-computing",
        "Title": "Heartbeat",
        "Description": "Successor to gridworks.ping. Includes structured liveness telemetry instead of just an empty round-trip.",
        "ReplacedBy": None,
        "PythonClassName": "GridworksHeartbeat",
        "MakeDataClass": True,
        "IsCac": False,
        "IsComponent": False,
    }, key_fn=lambda r: r["Name"])
    upsert_row(rb["TypeVersions"]["data"], {
        "Type": "gridworks.heartbeat",
        "Version": "000",
        "SchemaUrl": "https://schemas.electricity.works/types/gridworks.heartbeat/000",
        "Title": "Gridworks Heartbeat",
        "Description": "Periodic liveness signal carrying observed clock skew and queue-depth metrics.",
        "ExtraAllowed": False,
        "Status": "active",
        "Created": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Type"], r["Version"]))
    for idx, (an, fr, desc) in enumerate([
        ("FromGNodeAlias", "left.right.dot", "Sender's canonical alias."),
        ("HeartbeatTimestamp", "utc.iso8601.millis", "Wall-clock at signal emission."),
        ("ObservedSkewMs", None, "Observed offset vs upstream NTP, in ms."),
        ("QueueDepth", None, "Outbound queue depth at emission."),
    ]):
        upsert_row(rb["TypeAttributes"]["data"], {
            "TypeVersion": "gridworks.heartbeat/000",
            "AttributeName": an,
            "Idx": idx,
            "Description": desc,
            "Default": None,
            "IsRequired": True,
            "IsList": False,
            "PrimitiveType": "int" if fr is None else None,
            "FormatRef": fr,
            "EnumVersionRef": None,
            "SubTypeVersionRef": None,
            "HelperRef": None,
            "RawJson": None,
        }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))

    # Now apply the retirements:
    for fmt in rb["Formats"]["data"]:
        if fmt["Name"] == "market.slot.name":
            fmt["ReplacedBy"] = "market.slot.handle"

    for enum in rb["Enums"]["data"]:
        if enum["Name"] == "relay.closed.or.open":
            enum["ReplacedBy"] = "relay.open.or.closed"

    for t in rb["Types"]["data"]:
        if t["Name"] == "gridworks.ping":
            t["ReplacedBy"] = "gridworks.heartbeat"

    # ============================================================
    # M1 — Drafts
    # ============================================================
    # Draft TypeVersion: bid/001
    upsert_row(rb["TypeVersions"]["data"], {
        "Type": "bid",
        "Version": "001",
        "SchemaUrl": "https://schemas.electricity.works/types/bid/001",
        "Title": "bid (draft v001)",
        "Description": "Proposed evolution of bid/000. Adds explicit BidExpiry and an optional BidNotes free-text field. Also adopts market.slot.handle (the successor format) for MarketSlotName.",
        "ExtraAllowed": False,
        "Status": "draft",
        "Created": NOW,
        "LastModified": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Type"], r["Version"]))
    bid_001_attrs = [
        ("BidderAlias", "left.right.dot", None, None, None, "Canonical alias of the market participant submitting this bid.", True, False),
        ("MarketSlotName", "market.slot.handle", None, None, None, "Identifier of the market slot. Now uses the new market.slot.handle format (successor to market.slot.name).", True, False),
        ("PqPairs", None, None, "price.quantity.unitless/001", None, "Ordered list of price-quantity pairs.", True, True),
        ("PriceUnit", None, "market.price.unit/000", None, None, "Currency/unit for prices.", True, False),
        ("QuantityUnit", None, "market.quantity.unit/000", None, None, "Unit for quantities.", True, False),
        ("BidExpiry", "utc.iso8601.millis", None, None, None, "NEW in /001: hard expiry timestamp; bids must clear before this instant or be rejected.", True, False),
        ("BidNotes", None, None, None, None, "NEW in /001: optional free-text annotation, unstructured.", False, False),
    ]
    for idx, (an, fr, ev, sv, hr, desc, req, lst) in enumerate(bid_001_attrs):
        upsert_row(rb["TypeAttributes"]["data"], {
            "TypeVersion": "bid/001",
            "AttributeName": an,
            "Idx": idx,
            "Description": desc,
            "Default": None,
            "IsRequired": req,
            "IsList": lst,
            "PrimitiveType": "string" if (an == "BidNotes") else None,
            "FormatRef": fr,
            "EnumVersionRef": ev,
            "SubTypeVersionRef": sv,
            "HelperRef": hr,
            "RawJson": None,
        }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))
    upsert_row(rb["TypeAxioms"]["data"], {
        "TypeVersion": "bid/001",
        "Number": 1,
        "AxiomName": "ExpiryAfterMarketSlotEnd",
        "Statement": "BidExpiry SHALL be no later than the closing instant of MarketSlotName plus a tolerance window declared by the corresponding MarketType.",
    }, key_fn=lambda r: (r["TypeVersion"], r["AxiomName"]))

    # TypeUpgrade scaffolded for the bid/000 → bid/001 fork
    upsert_row(rb["TypeUpgrades"]["data"], {
        "FromTypeVersion": "bid/000",
        "ToTypeVersion": "bid/001",
        "Description": "000 -> 001: add BidExpiry (required), add BidNotes (optional), migrate MarketSlotName to market.slot.handle.",
        "RawScript": None,
    }, key_fn=lambda r: (r["FromTypeVersion"], r["ToTypeVersion"]))

    # Draft TypeVersion: data.channel.gt/003
    upsert_row(rb["TypeVersions"]["data"], {
        "Type": "data.channel.gt",
        "Version": "003",
        "SchemaUrl": "https://schemas.electricity.works/types/data.channel.gt/003",
        "Title": "Data Channel (draft v003)",
        "Description": "Adds RetentionWindowDays — channels become self-describing about their data-retention guarantees.",
        "ExtraAllowed": False,
        "Status": "draft",
        "Created": NOW,
        "LastModified": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Type"], r["Version"]))
    upsert_row(rb["TypeAttributes"]["data"], {
        "TypeVersion": "data.channel.gt/003",
        "AttributeName": "Name",
        "Idx": 0, "Description": "Channel name.", "Default": None, "IsRequired": True, "IsList": False,
        "PrimitiveType": None, "FormatRef": "spaceheat.name", "EnumVersionRef": None, "SubTypeVersionRef": None,
        "HelperRef": None, "RawJson": None,
    }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))
    upsert_row(rb["TypeAttributes"]["data"], {
        "TypeVersion": "data.channel.gt/003",
        "AttributeName": "RetentionWindowDays",
        "Idx": 1, "Description": "NEW in /003: how many days of samples this channel commits to keeping.",
        "Default": None, "IsRequired": True, "IsList": False, "PrimitiveType": "int",
        "FormatRef": None, "EnumVersionRef": None, "SubTypeVersionRef": None, "HelperRef": None, "RawJson": None,
    }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))

    # Draft TypeVersion: report.event/004
    upsert_row(rb["TypeVersions"]["data"], {
        "Type": "report.event",
        "Version": "004",
        "SchemaUrl": "https://schemas.electricity.works/types/report.event/004",
        "Title": "Report Event (draft v004)",
        "Description": "Adds Severity, an enumerated severity classification. Forks from /003 (current leaf).",
        "ExtraAllowed": False,
        "Status": "draft",
        "Created": NOW,
        "LastModified": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Type"], r["Version"]))
    upsert_row(rb["TypeAttributes"]["data"], {
        "TypeVersion": "report.event/004",
        "AttributeName": "EventName",
        "Idx": 0, "Description": "Short descriptive name.", "Default": None, "IsRequired": True, "IsList": False,
        "PrimitiveType": "string", "FormatRef": None, "EnumVersionRef": None, "SubTypeVersionRef": None,
        "HelperRef": None, "RawJson": None,
    }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))
    upsert_row(rb["TypeAttributes"]["data"], {
        "TypeVersion": "report.event/004",
        "AttributeName": "Severity",
        "Idx": 1, "Description": "NEW in /002: severity from a controlled vocabulary.",
        "Default": None, "IsRequired": True, "IsList": False, "PrimitiveType": None,
        "FormatRef": None, "EnumVersionRef": "fis.authorization.decision/000",
        "SubTypeVersionRef": None, "HelperRef": None, "RawJson": None,
    }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))

    # Draft EnumVersion: gw1.unit/002
    upsert_row(rb["EnumVersions"]["data"], {
        "Enum": "gw1.unit",
        "Version": "002",
        "SchemaUrl": "https://schemas.electricity.works/enums/gw1.unit/002",
        "Title": "GridWorks Unit (draft v002)",
        "Description": "Adds KiloWattHours and MegaWatts to the canonical unit set.",
        "DefaultSymbol": None,
        "Status": "draft",
        "Created": NOW,
        "LastModified": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Enum"], r["Version"]))
    for idx, sym, desc in [
        (0, "Unitless", "Dimensionless quantity."),
        (1, "W", "Watts."),
        (2, "Wh", "Watt-hours."),
        (3, "Celsius", "Degrees Celsius."),
        (4, "Gpm", "Gallons per minute."),
        (5, "KiloWattHours", "NEW in /002: kilowatt-hours, for accumulated energy reporting."),
        (6, "MegaWatts", "NEW in /002: megawatts, for utility-scale power."),
    ]:
        upsert_row(rb["EnumValues"]["data"], {
            "EnumVersion": "gw1.unit/002",
            "Symbol": sym,
            "Idx": idx,
            "Description": desc,
        }, key_fn=lambda r: (r["EnumVersion"], r["Symbol"]))

    # Draft EnumVersion: relay.closed.or.open/001  (note: this Word is being retired,
    # which makes for a good demo — a draft on a Word that's also retired)
    upsert_row(rb["EnumVersions"]["data"], {
        "Enum": "relay.closed.or.open",
        "Version": "001",
        "SchemaUrl": "https://schemas.electricity.works/enums/relay.closed.or.open/001",
        "Title": "Relay closed-or-open (draft v001 — Word being retired)",
        "Description": "Draft addition of Unknown, but the Word itself is being retired in favor of relay.open.or.closed. Demonstrates that drafts can exist on retired Words (their history is still legible).",
        "DefaultSymbol": None,
        "Status": "draft",
        "Created": NOW,
        "LastModified": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Enum"], r["Version"]))
    for idx, sym, desc in [
        (0, "Closed", "Relay is closed (current flowing)."),
        (1, "Open", "Relay is open (no current)."),
        (2, "Unknown", "Relay state is indeterminate."),
    ]:
        upsert_row(rb["EnumValues"]["data"], {
            "EnumVersion": "relay.closed.or.open/001",
            "Symbol": sym,
            "Idx": idx,
            "Description": desc,
        }, key_fn=lambda r: (r["EnumVersion"], r["Symbol"]))

    # ============================================================
    # M4 — Published artifacts for the 3 empty Owners
    # ============================================================
    # joe-strommen → Type `boundary.heartbeat/000`
    upsert_row(rb["Types"]["data"], {
        "Name": "boundary.heartbeat",
        "Owner": "joe-strommen",
        "Title": "Boundary Heartbeat",
        "Description": "Liveness signal exchanged across an org-to-org boundary (e.g. a federation peer).",
        "ReplacedBy": None,
        "PythonClassName": "BoundaryHeartbeat",
        "MakeDataClass": True,
        "IsCac": False,
        "IsComponent": False,
    }, key_fn=lambda r: r["Name"])
    upsert_row(rb["TypeVersions"]["data"], {
        "Type": "boundary.heartbeat",
        "Version": "000",
        "SchemaUrl": "https://schemas.electricity.works/types/boundary.heartbeat/000",
        "Title": "Boundary Heartbeat",
        "Description": "Periodic boundary liveness probe with monotonic sequence number.",
        "ExtraAllowed": False,
        "Status": "active",
        "Created": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Type"], r["Version"]))
    for idx, (an, fr, pt, desc) in enumerate([
        ("PeerAlias", "left.right.dot", None, "The peer org's alias on the other side of the boundary."),
        ("Sequence", None, "int", "Monotonically increasing sequence number."),
        ("EmittedAt", "utc.iso8601.millis", None, "When the heartbeat left the sender."),
    ]):
        upsert_row(rb["TypeAttributes"]["data"], {
            "TypeVersion": "boundary.heartbeat/000",
            "AttributeName": an,
            "Idx": idx,
            "Description": desc,
            "Default": None, "IsRequired": True, "IsList": False,
            "PrimitiveType": pt, "FormatRef": fr,
            "EnumVersionRef": None, "SubTypeVersionRef": None,
            "HelperRef": None, "RawJson": None,
        }, key_fn=lambda r: (r["TypeVersion"], r["AttributeName"]))

    # microerapower → Format `microera.feed.tag`
    upsert_row(rb["Formats"]["data"], {
        "Name": "microera.feed.tag",
        "Owner": "microerapower",
        "SchemaUrl": "https://schemas.electricity.works/formats/microera.feed.tag",
        "Title": "MicroEra feed tag",
        "Description": "Tag identifying a MicroEra data feed. Lowercase letters, digits, hyphens; up to 32 characters.",
        "ReplacedBy": None,
        "Pattern": "^[a-z0-9-]{3,32}$",
        "MinLength": 3,
        "MaxLength": 32,
        "JsonSchemaFormat": None,
        "Created": NOW,
        "RawJson": None,
    }, key_fn=lambda r: r["Name"])
    upsert_row(rb["FormatExamples"]["data"], {
        "Format": "microera.feed.tag",
        "Idx": 0,
        "IsCounter": False,
        "Value": "boston-grid-east",
        "Description": "A regional feed tag.",
    }, key_fn=lambda r: (r["Format"], r["Value"]))
    upsert_row(rb["FormatExamples"]["data"], {
        "Format": "microera.feed.tag",
        "Idx": 1,
        "IsCounter": True,
        "Value": "Boston-Grid-East",
        "Description": "Counter-example: uppercase not allowed.",
    }, key_fn=lambda r: (r["Format"], r["Value"]))

    # thomas-defauw → Enum `defauw.action/000` with values
    upsert_row(rb["Enums"]["data"], {
        "Name": "defauw.action",
        "Owner": "thomas-defauw",
        "EnumType": "open",
        "ValueType": "string",
        "Description": "Atomic actions in Thomas's signaling protocol.",
        "ReplacedBy": None,
        "RawJson": None,
    }, key_fn=lambda r: r["Name"])
    upsert_row(rb["EnumVersions"]["data"], {
        "Enum": "defauw.action",
        "Version": "000",
        "SchemaUrl": "https://schemas.electricity.works/enums/defauw.action/000",
        "Title": "DeFauw Action",
        "Description": "Initial release.",
        "DefaultSymbol": "Hold",
        "Status": "active",
        "Created": NOW,
        "RawJson": None,
    }, key_fn=lambda r: (r["Enum"], r["Version"]))
    for idx, sym, desc in [
        (0, "Hold", "Take no action."),
        (1, "Advance", "Advance to the next signal."),
        (2, "Retreat", "Step back one signal."),
        (3, "Reset", "Return to initial state."),
    ]:
        upsert_row(rb["EnumValues"]["data"], {
            "EnumVersion": "defauw.action/000",
            "Symbol": sym,
            "Idx": idx,
            "Description": desc,
        }, key_fn=lambda r: (r["EnumVersion"], r["Symbol"]))

    # ============================================================
    # M5 — EnumUpgrades + EnumUpgradeMappings
    # ============================================================
    # gw1.unit/000 → /001  (using existing rows; this is a previously-implicit upgrade)
    upsert_row(rb["EnumUpgrades"]["data"], {
        "FromEnumVersion": "gw1.unit/000",
        "ToEnumVersion": "gw1.unit/001",
        "Description": "000 -> 001: rename Btus to BTUs (case fix).",
        "RawScript": None,
    }, key_fn=lambda r: (r["FromEnumVersion"], r["ToEnumVersion"]))
    # Identity-mostly mappings — pull symbols from the EnumValues we already have
    gw1_unit_000_syms = {r["Symbol"] for r in rb["EnumValues"]["data"]
                         if r["EnumVersion"] == "gw1.unit/000"}
    gw1_unit_001_syms = {r["Symbol"] for r in rb["EnumValues"]["data"]
                         if r["EnumVersion"] == "gw1.unit/001"}
    for sym in sorted(gw1_unit_000_syms):
        target = sym if sym in gw1_unit_001_syms else None
        upsert_row(rb["EnumUpgradeMappings"]["data"], {
            "EnumUpgrade": "gw1.unit/000 -> gw1.unit/001",
            "FromSymbol": sym,
            "ToSymbol": target,
            "Description": "Identity carry-over." if target == sym else f"Renamed/removed: {sym}",
        }, key_fn=lambda r: (r["EnumUpgrade"], r["FromSymbol"]))

    # gw1.quantity/000 → /001
    upsert_row(rb["EnumUpgrades"]["data"], {
        "FromEnumVersion": "gw1.quantity/000",
        "ToEnumVersion": "gw1.quantity/001",
        "Description": "000 -> 001: split AveragePowerWatts into AveragePower and InstantaneousPower.",
        "RawScript": None,
    }, key_fn=lambda r: (r["FromEnumVersion"], r["ToEnumVersion"]))
    gw1_q_000_syms = {r["Symbol"] for r in rb["EnumValues"]["data"]
                      if r["EnumVersion"] == "gw1.quantity/000"}
    gw1_q_001_syms = {r["Symbol"] for r in rb["EnumValues"]["data"]
                      if r["EnumVersion"] == "gw1.quantity/001"}
    for sym in sorted(gw1_q_000_syms):
        target = sym if sym in gw1_q_001_syms else None
        upsert_row(rb["EnumUpgradeMappings"]["data"], {
            "EnumUpgrade": "gw1.quantity/000 -> gw1.quantity/001",
            "FromSymbol": sym,
            "ToSymbol": target,
            "Description": "Identity carry-over." if target == sym else f"Symbol removed/renamed: {sym}",
        }, key_fn=lambda r: (r["EnumUpgrade"], r["FromSymbol"]))

    # ============================================================
    # M6 — Fix the 2 existing Projections' null endpoints
    # ============================================================
    for p in rb["Projections"]["data"]:
        if p["Name"] == "Gw1UnitQuantityProjection":
            if p.get("FromEnumVersion") in (None, ""):
                p["FromEnumVersion"] = "gw1.quantity/001"
            if p.get("ToEnumVersion") in (None, ""):
                p["ToEnumVersion"] = "gw1.unit/001"
        if p["Name"] == "SpaceheatTelemetryQuantityProjection":
            if p.get("FromEnumVersion") in (None, ""):
                p["FromEnumVersion"] = "spaceheat.telemetry.name/007"
            if p.get("ToEnumVersion") in (None, ""):
                p["ToEnumVersion"] = "gw1.quantity/001"

    # ============================================================
    # M3 — Reconcile deprecation state with the upgrade graph (run last so it
    # sees all the upgrades created above).
    # A TypeVersion is `deprecated` iff some TypeUpgrade chain leads forward
    # from it to an `active` (non-draft) descendant. Equivalently: deprecated
    # iff there is an outgoing TypeUpgrade to a non-draft successor. We iterate
    # until convergence so multi-step chains (000→001→002) settle correctly.
    # ============================================================
    tv_by_name = {f"{tv['Type']}/{tv['Version']}": tv for tv in rb["TypeVersions"]["data"]}
    upgrades = rb["TypeUpgrades"]["data"]

    # First pass: any TV that's currently deprecated but has NO outgoing upgrade
    # at all gets restored to active (e.g. if an upgrade was removed).
    has_outgoing = {u["FromTypeVersion"] for u in upgrades}
    for name, tv in tv_by_name.items():
        if tv.get("Status") == "deprecated" and name not in has_outgoing:
            tv["Status"] = "active"
            tv["DeprecatedAt"] = None

    # Iterate to convergence: a FromTV becomes deprecated when its successor
    # is either active or already-deprecated (i.e. not draft).
    while True:
        changed = False
        for u in upgrades:
            from_tv = tv_by_name.get(u["FromTypeVersion"])
            to_tv = tv_by_name.get(u["ToTypeVersion"])
            if not from_tv or not to_tv:
                continue
            if from_tv.get("Status") == "active" and to_tv.get("Status") in ("active", "deprecated"):
                from_tv["Status"] = "deprecated"
                from_tv["DeprecatedAt"] = RECENT_DEPRECATION
                changed = True
        if not changed:
            break

    # ============================================================
    # Save
    # ============================================================
    RULEBOOK.write_text(json.dumps(rb, indent=2) + "\n")
    print("Mock data applied.")


if __name__ == "__main__":
    main()
