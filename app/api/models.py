"""Pydantic response models mirroring vw_* view columns.

Hand-rolled for Phase 2. Each model permits extra fields via ConfigDict so newly
added view columns flow through the API without churn while typed access stays
ergonomic on the headline columns.

TODO: replace with rulebook-emitters/python/out/ when that emitter graduates.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class _Row(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class Owner(_Row):
    owners_id: str
    name: str
    owner_type: str | None = None
    contact: str | None = None
    website: str | None = None
    github: str | None = None
    organization: str | None = None
    description: str | None = None
    support_policy: str | None = None
    license: str | None = None
    is_organization: bool | None = None
    has_github: bool | None = None
    format_count: int | None = None
    enum_count: int | None = None
    type_count: int | None = None
    draft_type_version_count: int | None = None
    active_type_version_count: int | None = None
    deprecated_type_version_count: int | None = None
    draft_enum_version_count: int | None = None
    active_enum_version_count: int | None = None
    deprecated_enum_version_count: int | None = None
    retired_type_count: int | None = None
    retired_enum_count: int | None = None
    retired_format_count: int | None = None
    has_open_drafts: bool | None = None
    has_published_artifacts: bool | None = None
    latest_type_version_at: datetime | None = None


class Type(_Row):
    types_id: str
    name: str
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    owner_name: str | None = None
    replaced_by: str | None = None
    is_retired: bool | None = None
    version_count: int | None = None
    active_version_count: int | None = None
    draft_version_count: int | None = None
    deprecated_version_count: int | None = None
    has_drafts: bool | None = None
    latest_version: str | None = None


class TypeVersion(_Row):
    type_versions_id: str
    name: str
    type: str
    version: str
    schema_url: str | None = None
    title: str | None = None
    description: str | None = None
    extra_allowed: bool | None = None
    status: str | None = None
    created: datetime | None = None
    is_active: bool | None = None
    is_deprecated: bool | None = None
    is_draft: bool | None = None
    is_closed: bool | None = None
    attribute_count: int | None = None
    required_attribute_count: int | None = None
    axiom_count: int | None = None
    example_count: int | None = None
    outgoing_upgrade_count: int | None = None
    incoming_upgrade_count: int | None = None
    originated_helper_count: int | None = None
    total_subtype_usage_count: int | None = None
    is_used_as_subtype: bool | None = None
    has_incoming_upgrade: bool | None = None
    has_outgoing_upgrade: bool | None = None
    is_root: bool | None = None
    is_leaf: bool | None = None
    originates_helpers: bool | None = None
    owner_name: str | None = None
    word_title: str | None = None
    word_is_retired: bool | None = None
    last_modified: datetime | None = None
    promoted_at: datetime | None = None
    deprecated_at: datetime | None = None
    stale_reference_count: int | None = None
    has_stale_references: bool | None = None
    is_promotable: bool | None = None


class TypeAttribute(_Row):
    type_attributes_id: str
    name: str
    type_version: str | None = None
    attribute_name: str | None = None
    idx: int | None = None
    description: str | None = None
    default: str | None = None
    is_required: bool | None = None
    is_optional: bool | None = None
    has_default: bool | None = None
    is_list: bool | None = None
    primitive_type: str | None = None
    format_ref: str | None = None
    enum_version_ref: str | None = None
    sub_type_version_ref: str | None = None
    helper_ref: str | None = None
    ref_kind: str | None = None
    # Per-attribute "this ref is broken" warnings (APP_PLAN §10).
    ref_format_is_retired: bool | None = None
    ref_enum_is_active: bool | None = None
    ref_enum_is_draft: bool | None = None
    ref_enum_word_is_retired: bool | None = None
    ref_subtype_is_active: bool | None = None
    ref_subtype_is_draft: bool | None = None
    ref_subtype_word_is_retired: bool | None = None
    ref_is_stale: bool | None = None


class TypeAxiom(_Row):
    type_axioms_id: str
    name: str
    type_version: str | None = None
    statement: str | None = None
    idx: int | None = None


class TypeExample(_Row):
    type_examples_id: str
    name: str
    type_version: str | None = None
    example_json: str | None = None


class Enum(_Row):
    enums_id: str
    name: str
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    owner_name: str | None = None
    replaced_by: str | None = None
    is_retired: bool | None = None
    version_count: int | None = None


class EnumVersion(_Row):
    enum_versions_id: str
    name: str
    enum: str
    version: str
    title: str | None = None
    description: str | None = None
    status: str | None = None
    is_active: bool | None = None
    is_deprecated: bool | None = None
    is_draft: bool | None = None
    value_count: int | None = None
    total_attribute_usage_count: int | None = None
    owner_name: str | None = None


class EnumValue(_Row):
    enum_values_id: str
    name: str
    enum_version: str | None = None
    title: str | None = None
    description: str | None = None
    idx: int | None = None


class Format(_Row):
    formats_id: str
    name: str
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    owner_name: str | None = None
    pattern: str | None = None
    json_schema_format: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    replaced_by: str | None = None
    is_retired: bool | None = None
    total_usage_count: int | None = None


class FormatExample(_Row):
    format_examples_id: str
    name: str
    format: str | None = None
    value: str | None = None
    is_counter: bool | None = None
    example_kind: str | None = None


class TypeHelper(_Row):
    type_helpers_id: str
    name: str
    origin_type_version: str | None = None
    origin_path: str | None = None
    extra_allowed: bool | None = None
    is_closed: bool | None = None
    total_usage_count: int | None = None


class TypeHelperAttribute(_Row):
    type_helper_attributes_id: str
    name: str
    type_helper: str | None = None
    attribute_name: str | None = None
    idx: int | None = None
    description: str | None = None
    is_required: bool | None = None
    is_list: bool | None = None
    primitive_type: str | None = None
    format_ref: str | None = None
    enum_version_ref: str | None = None
    sub_type_version_ref: str | None = None
    helper_ref: str | None = None
    ref_kind: str | None = None
    # Mirrors TypeAttribute's stale-ref calc fields where the helper view exposes them.
    ref_format_is_retired: bool | None = None
    ref_enum_is_draft: bool | None = None
    ref_enum_word_is_retired: bool | None = None
    ref_subtype_is_draft: bool | None = None
    ref_subtype_word_is_retired: bool | None = None
    ref_is_stale: bool | None = None


class Projection(_Row):
    projections_id: str
    name: str
    from_enum_version: str | None = None
    to_enum_version: str | None = None


class ProjectionMapping(_Row):
    projection_mappings_id: str
    name: str
    projection: str | None = None
    from_value: str | None = None
    to_value: str | None = None


class TypeUpgrade(_Row):
    type_upgrades_id: str
    name: str
    from_type_version: str | None = None
    to_type_version: str | None = None


class TypeUpgradeOp(_Row):
    type_upgrade_ops_id: str
    name: str
    type_upgrade: str | None = None
    op_kind: str | None = None
    idx: int | None = None


class EnumUpgrade(_Row):
    enum_upgrades_id: str
    name: str
    from_enum_version: str | None = None
    to_enum_version: str | None = None


class EnumUpgradeMapping(_Row):
    enum_upgrade_mappings_id: str
    name: str
    enum_upgrade: str | None = None
    from_value: str | None = None
    to_value: str | None = None


class SearchHit(BaseModel):
    table: str
    id: str
    name: str
    title: str | None = None
    description: str | None = None
    snippet: str | None = None


class TableSummary(BaseModel):
    table: str
    row_count: int


class HealthResponse(BaseModel):
    ok: bool
    db: bool
    rulebook: bool
    tables: list[TableSummary]
