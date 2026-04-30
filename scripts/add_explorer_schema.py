"""
Add Explorer-driven calc/aggregation/lookup fields + raw lifecycle timestamps to
the Sema rulebook. Run once, then run `effortless build`. This script is
idempotent: existing fields with the same name are skipped.
"""

import json
from pathlib import Path

RULEBOOK = Path(__file__).resolve().parents[1] / "effortless-rulebook" / "effortless-rulebook.json"


def field(name, datatype, type_, nullable, description, formula=None, related_to=None):
    f = {
        "name": name,
        "datatype": datatype,
        "type": type_,
        "nullable": nullable,
        "Description": description,
    }
    if formula is not None:
        f["formula"] = formula
    if related_to is not None:
        f["RelatedTo"] = related_to
    return f


def append_fields(table_schema, new_fields, before_field=None):
    existing = {f["name"] for f in table_schema}
    if before_field:
        idx = next((i for i, f in enumerate(table_schema) if f["name"] == before_field), len(table_schema))
    else:
        idx = len(table_schema)
    inserted = 0
    for f in new_fields:
        if f["name"] in existing:
            continue
        table_schema.insert(idx + inserted, f)
        inserted += 1
    return inserted


def main():
    rb = json.loads(RULEBOOK.read_text())

    # ============================================================
    # TypeVersions — passthrough lookups + lifecycle timestamps + promote-gating
    # ============================================================
    tv = rb["TypeVersions"]["schema"]
    append_fields(tv, [
        field("OwnerName", "string", "lookup", True,
              "Owner of this Definition's Word, passed through from Types.Owner. Lets list views render owner without joining.",
              formula="=INDEX(Types!{{Owner}}, MATCH({{Type}}, Types!{{Name}}, 0))"),
        field("WordTitle", "string", "lookup", True,
              "Title of this Definition's Word, passed through from Types.Title. Used in breadcrumbs.",
              formula="=INDEX(Types!{{Title}}, MATCH({{Type}}, Types!{{Name}}, 0))"),
        field("WordIsRetired", "boolean", "lookup", True,
              "Whether this Definition's Word is retired (Types.IsRetired). Drives the red strike-through pill in §4 — distinct from version-level deprecation.",
              formula="=INDEX(Types!{{IsRetired}}, MATCH({{Type}}, Types!{{Name}}, 0))"),
        field("LastModified", "datetime", "raw", True,
              "Most recent edit to this Definition or any of its child rows. Null until the editor lands. Drives Activity-feed sort."),
        field("PromotedAt", "datetime", "raw", True,
              "When Status flipped from draft to active. Null for never-promoted drafts. Activity feed renders 'promoted on...' distinct from 'created on...'."),
        field("DeprecatedAt", "datetime", "raw", True,
              "When Status flipped from active to deprecated. Null while still active or while still draft."),
        field("StaleReferenceCount", "integer", "aggregation", False,
              "Number of TypeAttributes on this Definition whose ref points at a retired/deprecated/draft target. Drives §7 promote-gating.",
              formula="=COUNTIFS(TypeAttributes!{{TypeVersion}}, TypeVersions!{{Name}}, TypeAttributes!{{RefIsStale}}, TRUE())"),
        field("HasStaleReferences", "boolean", "calculated", False,
              "True iff any of this Definition's attribute refs are stale.",
              formula="=IF({{StaleReferenceCount}}>0, TRUE(), FALSE())"),
        field("IsPromotable", "boolean", "calculated", False,
              "True iff this draft Definition can be promoted: it is a draft, has no stale references, and has at least one attribute. Gates the Promote CTA in §7.",
              formula="=IF(AND({{IsDraft}}, NOT({{HasStaleReferences}}), {{AttributeCount}}>0), TRUE(), FALSE())"),
    ])

    # ============================================================
    # EnumVersions — passthrough lookups + lifecycle timestamps + promote-gating
    # ============================================================
    ev = rb["EnumVersions"]["schema"]
    append_fields(ev, [
        field("OwnerName", "string", "lookup", True,
              "Owner of this EnumVersion's Word, passed through from Enums.Owner.",
              formula="=INDEX(Enums!{{Owner}}, MATCH({{Enum}}, Enums!{{Name}}, 0))"),
        field("WordIsRetired", "boolean", "lookup", True,
              "Whether this EnumVersion's Word is retired (Enums.IsRetired). Drives §4 red strike-through.",
              formula="=INDEX(Enums!{{IsRetired}}, MATCH({{Enum}}, Enums!{{Name}}, 0))"),
        field("WordDescription", "string", "lookup", True,
              "Description of the parent Enum.",
              formula="=INDEX(Enums!{{Description}}, MATCH({{Enum}}, Enums!{{Name}}, 0))"),
        field("LastModified", "datetime", "raw", True,
              "Most recent edit to this EnumVersion or its child EnumValues."),
        field("PromotedAt", "datetime", "raw", True,
              "When Status flipped from draft to active."),
        field("DeprecatedAt", "datetime", "raw", True,
              "When Status flipped from active to deprecated."),
        field("IsPromotable", "boolean", "calculated", False,
              "True iff this draft EnumVersion can be promoted: it is a draft and has at least one symbol.",
              formula="=IF(AND({{IsDraft}}, {{ValueCount}}>0), TRUE(), FALSE())"),
    ])

    # ============================================================
    # TypeAttributes — reference-staleness via per-kind lookups + composite calc
    # ============================================================
    ta = rb["TypeAttributes"]["schema"]
    append_fields(ta, [
        field("RefFormatIsRetired", "boolean", "lookup", True,
              "Whether the FormatRef target is retired. Null when FormatRef is unset.",
              formula="=INDEX(Formats!{{IsRetired}}, MATCH({{FormatRef}}, Formats!{{Name}}, 0))"),
        field("RefEnumIsActive", "boolean", "lookup", True,
              "Whether the EnumVersionRef target has Status='active'. Null when EnumVersionRef is unset.",
              formula="=INDEX(EnumVersions!{{IsActive}}, MATCH({{EnumVersionRef}}, EnumVersions!{{Name}}, 0))"),
        field("RefEnumIsDraft", "boolean", "lookup", True,
              "Whether the EnumVersionRef target is still a draft. Promoting a draft TypeVersion that points at a draft EnumVersion is not allowed.",
              formula="=INDEX(EnumVersions!{{IsDraft}}, MATCH({{EnumVersionRef}}, EnumVersions!{{Name}}, 0))"),
        field("RefEnumWordIsRetired", "boolean", "lookup", True,
              "Whether the EnumVersionRef's Word is retired.",
              formula="=INDEX(EnumVersions!{{WordIsRetired}}, MATCH({{EnumVersionRef}}, EnumVersions!{{Name}}, 0))"),
        field("RefSubtypeIsActive", "boolean", "lookup", True,
              "Whether the SubTypeVersionRef target has Status='active'.",
              formula="=INDEX(TypeVersions!{{IsActive}}, MATCH({{SubTypeVersionRef}}, TypeVersions!{{Name}}, 0))"),
        field("RefSubtypeIsDraft", "boolean", "lookup", True,
              "Whether the SubTypeVersionRef target is still a draft.",
              formula="=INDEX(TypeVersions!{{IsDraft}}, MATCH({{SubTypeVersionRef}}, TypeVersions!{{Name}}, 0))"),
        field("RefSubtypeWordIsRetired", "boolean", "lookup", True,
              "Whether the SubTypeVersionRef's Word is retired.",
              formula="=INDEX(TypeVersions!{{WordIsRetired}}, MATCH({{SubTypeVersionRef}}, TypeVersions!{{Name}}, 0))"),
        field("RefIsStale", "boolean", "calculated", False,
              "True iff this attribute's reference points at a retired Word, a deprecated/draft EnumVersion or TypeVersion. Rolls up into TypeVersions.HasStaleReferences and gates promote.",
              formula="=IF(OR({{RefFormatIsRetired}}=TRUE(), {{RefEnumIsDraft}}=TRUE(), {{RefEnumWordIsRetired}}=TRUE(), {{RefSubtypeIsDraft}}=TRUE(), {{RefSubtypeWordIsRetired}}=TRUE()), TRUE(), FALSE())"),
    ])

    # ============================================================
    # TypeHelperAttributes — same staleness fields (mirror)
    # ============================================================
    tha = rb["TypeHelperAttributes"]["schema"]
    append_fields(tha, [
        field("RefFormatIsRetired", "boolean", "lookup", True,
              "Whether the FormatRef target is retired.",
              formula="=INDEX(Formats!{{IsRetired}}, MATCH({{FormatRef}}, Formats!{{Name}}, 0))"),
        field("RefEnumIsDraft", "boolean", "lookup", True,
              "Whether the EnumVersionRef target is still a draft.",
              formula="=INDEX(EnumVersions!{{IsDraft}}, MATCH({{EnumVersionRef}}, EnumVersions!{{Name}}, 0))"),
        field("RefEnumWordIsRetired", "boolean", "lookup", True,
              "Whether the EnumVersionRef's Word is retired.",
              formula="=INDEX(EnumVersions!{{WordIsRetired}}, MATCH({{EnumVersionRef}}, EnumVersions!{{Name}}, 0))"),
        field("RefSubtypeIsDraft", "boolean", "lookup", True,
              "Whether the SubTypeVersionRef target is still a draft.",
              formula="=INDEX(TypeVersions!{{IsDraft}}, MATCH({{SubTypeVersionRef}}, TypeVersions!{{Name}}, 0))"),
        field("RefSubtypeWordIsRetired", "boolean", "lookup", True,
              "Whether the SubTypeVersionRef's Word is retired.",
              formula="=INDEX(TypeVersions!{{WordIsRetired}}, MATCH({{SubTypeVersionRef}}, TypeVersions!{{Name}}, 0))"),
        field("RefIsStale", "boolean", "calculated", False,
              "True iff this helper attribute's reference points at a retired/deprecated/draft target.",
              formula="=IF(OR({{RefFormatIsRetired}}=TRUE(), {{RefEnumIsDraft}}=TRUE(), {{RefEnumWordIsRetired}}=TRUE(), {{RefSubtypeIsDraft}}=TRUE(), {{RefSubtypeWordIsRetired}}=TRUE()), TRUE(), FALSE())"),
    ])

    # ============================================================
    # Types — Word-level rollups
    # ============================================================
    t = rb["Types"]["schema"]
    append_fields(t, [
        field("DraftVersionCount", "integer", "aggregation", False,
              "Number of TypeVersions of this Word with Status='draft'. Drives 'drafts open' badge on Word cards.",
              formula="=COUNTIFS(TypeVersions!{{Type}}, Types!{{Name}}, TypeVersions!{{IsDraft}}, TRUE())"),
        field("ActiveVersionCount", "integer", "aggregation", False,
              "Number of active TypeVersions.",
              formula="=COUNTIFS(TypeVersions!{{Type}}, Types!{{Name}}, TypeVersions!{{IsActive}}, TRUE())"),
        field("DeprecatedVersionCount", "integer", "aggregation", False,
              "Number of deprecated TypeVersions.",
              formula="=COUNTIFS(TypeVersions!{{Type}}, Types!{{Name}}, TypeVersions!{{IsDeprecated}}, TRUE())"),
        field("HasDrafts", "boolean", "calculated", False,
              "True iff this Word has at least one draft Definition. Drives the amber 'drafts open' badge on Word rows.",
              formula="=IF({{DraftVersionCount}}>0, TRUE(), FALSE())"),
        field("FirstCreated", "datetime", "aggregation", True,
              "When the first Definition for this Word was created. Drives 'Word age' displays.",
              formula="=MINIFS(TypeVersions!{{Created}}, TypeVersions!{{Type}}, Types!{{Name}})"),
        field("LastModified", "datetime", "aggregation", True,
              "Latest TypeVersions.Created among this Word's Definitions. Drives 'recently active' sort.",
              formula="=MAXIFS(TypeVersions!{{Created}}, TypeVersions!{{Type}}, Types!{{Name}})"),
    ])

    # ============================================================
    # Enums — same Word-level rollups
    # ============================================================
    e = rb["Enums"]["schema"]
    append_fields(e, [
        field("DraftVersionCount", "integer", "aggregation", False,
              "Number of EnumVersions of this Word with Status='draft'.",
              formula="=COUNTIFS(EnumVersions!{{Enum}}, Enums!{{Name}}, EnumVersions!{{IsDraft}}, TRUE())"),
        field("ActiveVersionCount", "integer", "aggregation", False,
              "Number of active EnumVersions.",
              formula="=COUNTIFS(EnumVersions!{{Enum}}, Enums!{{Name}}, EnumVersions!{{IsActive}}, TRUE())"),
        field("DeprecatedVersionCount", "integer", "aggregation", False,
              "Number of deprecated EnumVersions.",
              formula="=COUNTIFS(EnumVersions!{{Enum}}, Enums!{{Name}}, EnumVersions!{{IsDeprecated}}, TRUE())"),
        field("HasDrafts", "boolean", "calculated", False,
              "True iff this Word has at least one draft Definition.",
              formula="=IF({{DraftVersionCount}}>0, TRUE(), FALSE())"),
        field("FirstCreated", "datetime", "aggregation", True,
              "When the first EnumVersion for this Word was created.",
              formula="=MINIFS(EnumVersions!{{Created}}, EnumVersions!{{Enum}}, Enums!{{Name}})"),
        field("LastModified", "datetime", "aggregation", True,
              "Latest EnumVersions.Created among this Word's Definitions.",
              formula="=MAXIFS(EnumVersions!{{Created}}, EnumVersions!{{Enum}}, Enums!{{Name}})"),
    ])

    # ============================================================
    # Owners — vocabulary-card rollups (depend on TypeVersions.OwnerName, EnumVersions.OwnerName)
    # ============================================================
    o = rb["Owners"]["schema"]
    append_fields(o, [
        field("DraftTypeVersionCount", "integer", "aggregation", False,
              "Number of draft TypeVersions across all this owner's Words. Drives §7 'drafts open: N' badge on the Vocabularies grid.",
              formula="=COUNTIFS(TypeVersions!{{OwnerName}}, Owners!{{Name}}, TypeVersions!{{IsDraft}}, TRUE())"),
        field("ActiveTypeVersionCount", "integer", "aggregation", False,
              "Number of active TypeVersions.",
              formula="=COUNTIFS(TypeVersions!{{OwnerName}}, Owners!{{Name}}, TypeVersions!{{IsActive}}, TRUE())"),
        field("DeprecatedTypeVersionCount", "integer", "aggregation", False,
              "Number of deprecated TypeVersions.",
              formula="=COUNTIFS(TypeVersions!{{OwnerName}}, Owners!{{Name}}, TypeVersions!{{IsDeprecated}}, TRUE())"),
        field("DraftEnumVersionCount", "integer", "aggregation", False,
              "Number of draft EnumVersions across this owner's Enums.",
              formula="=COUNTIFS(EnumVersions!{{OwnerName}}, Owners!{{Name}}, EnumVersions!{{IsDraft}}, TRUE())"),
        field("ActiveEnumVersionCount", "integer", "aggregation", False,
              "Number of active EnumVersions.",
              formula="=COUNTIFS(EnumVersions!{{OwnerName}}, Owners!{{Name}}, EnumVersions!{{IsActive}}, TRUE())"),
        field("DeprecatedEnumVersionCount", "integer", "aggregation", False,
              "Number of deprecated EnumVersions.",
              formula="=COUNTIFS(EnumVersions!{{OwnerName}}, Owners!{{Name}}, EnumVersions!{{IsDeprecated}}, TRUE())"),
        field("RetiredTypeCount", "integer", "aggregation", False,
              "Number of retired Types (Words). Drives the red-strike count on the Vocabulary card.",
              formula="=COUNTIFS(Types!{{Owner}}, Owners!{{Name}}, Types!{{IsRetired}}, TRUE())"),
        field("RetiredEnumCount", "integer", "aggregation", False,
              "Number of retired Enums (Words).",
              formula="=COUNTIFS(Enums!{{Owner}}, Owners!{{Name}}, Enums!{{IsRetired}}, TRUE())"),
        field("RetiredFormatCount", "integer", "aggregation", False,
              "Number of retired Formats.",
              formula="=COUNTIFS(Formats!{{Owner}}, Owners!{{Name}}, Formats!{{IsRetired}}, TRUE())"),
        field("HasOpenDrafts", "boolean", "calculated", False,
              "True iff this owner has any draft Type or Enum versions. Drives the amber dot on the Vocabularies card.",
              formula="=IF(OR({{DraftTypeVersionCount}}>0, {{DraftEnumVersionCount}}>0), TRUE(), FALSE())"),
        field("HasPublishedArtifacts", "boolean", "calculated", False,
              "True iff this owner has any artifacts at all (Types, Enums, or Formats). Drives empty-state vs populated rendering.",
              formula="=IF(OR({{TypeCount}}>0, {{EnumCount}}>0, {{FormatCount}}>0), TRUE(), FALSE())"),
        field("LatestTypeVersionAt", "datetime", "aggregation", True,
              "Most recent TypeVersions.Created among this owner's Words.",
              formula="=MAXIFS(TypeVersions!{{Created}}, TypeVersions!{{OwnerName}}, Owners!{{Name}})"),
        field("LatestEnumVersionAt", "datetime", "aggregation", True,
              "Most recent EnumVersions.Created among this owner's Enums.",
              formula="=MAXIFS(EnumVersions!{{Created}}, EnumVersions!{{OwnerName}}, Owners!{{Name}})"),
        field("LatestFormatAt", "datetime", "aggregation", True,
              "Most recent Formats.Created among this owner's Formats.",
              formula="=MAXIFS(Formats!{{Created}}, Formats!{{Owner}}, Owners!{{Name}})"),
    ])

    # ============================================================
    # Formats — owner passthrough for symmetry
    # ============================================================
    f = rb["Formats"]["schema"]
    append_fields(f, [
        field("OwnerName", "string", "lookup", True,
              "Owner of this Format, passed through from Formats.Owner. Symmetry with TypeVersions.OwnerName / EnumVersions.OwnerName so list views render owner uniformly.",
              formula="=INDEX(Owners!{{Name}}, MATCH({{Owner}}, Owners!{{Name}}, 0))"),
    ])

    # ============================================================
    # TypeHelpers — origin-context lookups
    # ============================================================
    th = rb["TypeHelpers"]["schema"]
    append_fields(th, [
        field("OriginOwnerName", "string", "lookup", True,
              "Owner of the helper's origin Definition.",
              formula="=INDEX(TypeVersions!{{OwnerName}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("OriginTypeName", "string", "lookup", True,
              "Word name of the helper's origin Definition.",
              formula="=INDEX(TypeVersions!{{Type}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("IsOriginDraft", "boolean", "lookup", True,
              "Whether the origin Definition is still a draft. Gates the 'Edit helper' CTA in §9c.",
              formula="=INDEX(TypeVersions!{{IsDraft}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("IsOriginActive", "boolean", "lookup", True,
              "Whether the origin Definition is active.",
              formula="=INDEX(TypeVersions!{{IsActive}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("IsOriginDeprecated", "boolean", "lookup", True,
              "Whether the origin Definition is deprecated.",
              formula="=INDEX(TypeVersions!{{IsDeprecated}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("OriginWordIsRetired", "boolean", "lookup", True,
              "Whether the origin Definition's Word is retired. Helpers inherit retirement of their origin Word.",
              formula="=INDEX(TypeVersions!{{WordIsRetired}}, MATCH({{OriginTypeVersion}}, TypeVersions!{{Name}}, 0))"),
    ])

    # ============================================================
    # Projections — endpoint-context lookups
    # ============================================================
    p = rb["Projections"]["schema"]
    append_fields(p, [
        field("FromOwnerName", "string", "lookup", True,
              "Owner of the FromEnumVersion.",
              formula="=INDEX(EnumVersions!{{OwnerName}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("ToOwnerName", "string", "lookup", True,
              "Owner of the ToEnumVersion.",
              formula="=INDEX(EnumVersions!{{OwnerName}}, MATCH({{ToEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("FromEnumName", "string", "lookup", True,
              "Enum name of the FromEnumVersion.",
              formula="=INDEX(EnumVersions!{{Enum}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("ToEnumName", "string", "lookup", True,
              "Enum name of the ToEnumVersion.",
              formula="=INDEX(EnumVersions!{{Enum}}, MATCH({{ToEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("FromIsDraft", "boolean", "lookup", True,
              "Whether the FromEnumVersion is still a draft.",
              formula="=INDEX(EnumVersions!{{IsDraft}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("ToIsDraft", "boolean", "lookup", True,
              "Whether the ToEnumVersion is still a draft.",
              formula="=INDEX(EnumVersions!{{IsDraft}}, MATCH({{ToEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("HasDraftEndpoints", "boolean", "calculated", False,
              "True iff either endpoint EnumVersion is still a draft.",
              formula="=IF(OR({{FromIsDraft}}=TRUE(), {{ToIsDraft}}=TRUE()), TRUE(), FALSE())"),
        field("IsCrossOwner", "boolean", "calculated", False,
              "True iff the projection crosses two different owners' enums (a meaningful editorial signal).",
              formula="=IF({{FromOwnerName}}<>{{ToOwnerName}}, TRUE(), FALSE())"),
        field("IsCrossEnum", "boolean", "calculated", False,
              "True iff the projection crosses two different Enums (vs versions of the same Enum).",
              formula="=IF({{FromEnumName}}<>{{ToEnumName}}, TRUE(), FALSE())"),
    ])

    # ============================================================
    # TypeUpgrades — chain validation lookups
    # ============================================================
    tu = rb["TypeUpgrades"]["schema"]
    append_fields(tu, [
        field("FromWord", "string", "lookup", True,
              "Word name of FromTypeVersion (should equal ToWord — IsCrossWord catches violations).",
              formula="=INDEX(TypeVersions!{{Type}}, MATCH({{FromTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("ToWord", "string", "lookup", True,
              "Word name of ToTypeVersion.",
              formula="=INDEX(TypeVersions!{{Type}}, MATCH({{ToTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("FromVersion", "string", "lookup", True,
              "Version string (e.g. '000') of FromTypeVersion.",
              formula="=INDEX(TypeVersions!{{Version}}, MATCH({{FromTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("ToVersion", "string", "lookup", True,
              "Version string (e.g. '001') of ToTypeVersion.",
              formula="=INDEX(TypeVersions!{{Version}}, MATCH({{ToTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("OwnerName", "string", "lookup", True,
              "Owner of the upgrade (passes through FromTypeVersion).",
              formula="=INDEX(TypeVersions!{{OwnerName}}, MATCH({{FromTypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("IsCrossWord", "boolean", "calculated", False,
              "True iff the upgrade crosses two different Words — should always be FALSE; flags malformed upgrades.",
              formula="=IF({{FromWord}}<>{{ToWord}}, TRUE(), FALSE())"),
    ])

    # ============================================================
    # EnumUpgrades — chain validation (mirror)
    # ============================================================
    eu = rb["EnumUpgrades"]["schema"]
    append_fields(eu, [
        field("FromWord", "string", "lookup", True,
              "Enum name of FromEnumVersion.",
              formula="=INDEX(EnumVersions!{{Enum}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("ToWord", "string", "lookup", True,
              "Enum name of ToEnumVersion.",
              formula="=INDEX(EnumVersions!{{Enum}}, MATCH({{ToEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("FromVersion", "string", "lookup", True,
              "Version of FromEnumVersion.",
              formula="=INDEX(EnumVersions!{{Version}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("ToVersion", "string", "lookup", True,
              "Version of ToEnumVersion.",
              formula="=INDEX(EnumVersions!{{Version}}, MATCH({{ToEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("OwnerName", "string", "lookup", True,
              "Owner of the upgrade.",
              formula="=INDEX(EnumVersions!{{OwnerName}}, MATCH({{FromEnumVersion}}, EnumVersions!{{Name}}, 0))"),
        field("IsCrossWord", "boolean", "calculated", False,
              "True iff the upgrade crosses two different Enum Words — flags malformed upgrades.",
              formula="=IF({{FromWord}}<>{{ToWord}}, TRUE(), FALSE())"),
    ])

    # ============================================================
    # TypeAxioms / TypeExamples / EnumValues / FormatExamples — small storytelling sugar
    # ============================================================
    tax = rb["TypeAxioms"]["schema"]
    append_fields(tax, [
        field("OwnerName", "string", "lookup", True,
              "Owner passthrough via TypeVersion → Type → Owner.",
              formula="=INDEX(TypeVersions!{{OwnerName}}, MATCH({{TypeVersion}}, TypeVersions!{{Name}}, 0))"),
        field("WordIsRetired", "boolean", "lookup", True,
              "True iff the parent Definition's Word is retired (axiom inherits visual retirement).",
              formula="=INDEX(TypeVersions!{{WordIsRetired}}, MATCH({{TypeVersion}}, TypeVersions!{{Name}}, 0))"),
    ])

    tex = rb["TypeExamples"]["schema"]
    append_fields(tex, [
        field("OwnerName", "string", "lookup", True,
              "Owner passthrough.",
              formula="=INDEX(TypeVersions!{{OwnerName}}, MATCH({{TypeVersion}}, TypeVersions!{{Name}}, 0))"),
    ])

    # ============================================================
    # Save
    # ============================================================
    RULEBOOK.write_text(json.dumps(rb, indent=2) + "\n")
    print("Schema additions applied.")


if __name__ == "__main__":
    main()
