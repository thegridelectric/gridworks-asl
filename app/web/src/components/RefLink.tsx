import { Link } from "react-router-dom";

/**
 * Renders a real link for any of the four polymorphic refs on a TypeAttribute
 * (or TypeHelperAttribute). Falls back to a primitive label when no FK is set.
 *
 * Per APP_PLAN §10, exactly one of these is populated; the calc field
 * `ref_kind` resolves which one. We trust ref_kind when present and fall
 * back to picking the first non-null FK otherwise.
 */
export interface RefLinkProps {
  refKind?: string | null;
  primitiveType?: string | null;
  formatRef?: string | null;
  enumVersionRef?: string | null;
  subTypeVersionRef?: string | null;
  helperRef?: string | null;
  isList?: boolean | null;
  isStale?: boolean | null;
}

function splitVersion(slashName: string): { name: string; version: string } | null {
  const idx = slashName.lastIndexOf("/");
  if (idx <= 0) return null;
  return { name: slashName.slice(0, idx), version: slashName.slice(idx + 1) };
}

export function RefLink(props: RefLinkProps) {
  const {
    refKind,
    primitiveType,
    formatRef,
    enumVersionRef,
    subTypeVersionRef,
    helperRef,
    isList,
    isStale,
  } = props;

  const wrap = (inner: React.ReactNode, href: string) => (
    <span className={isStale ? "ref ref-stale" : "ref"}>
      <Link to={href}>{inner}</Link>
      {isList && <span className="ref-list">[]</span>}
      {isStale && <span className="ref-stale-marker" title="Stale reference (target retired/replaced)">!</span>}
    </span>
  );

  if (refKind === "format" || (!refKind && formatRef)) {
    if (!formatRef) return <em>format (unset)</em>;
    return wrap(<>{formatRef} <span className="ref-kind">format</span></>, `/formats/${formatRef}`);
  }

  if (refKind === "enum" || (!refKind && enumVersionRef)) {
    if (!enumVersionRef) return <em>enum (unset)</em>;
    const split = splitVersion(enumVersionRef);
    const href = split
      ? `/enums/${split.name}/v/${split.version}`
      : `/enums/${enumVersionRef}`;
    return wrap(<>{enumVersionRef} <span className="ref-kind">enum</span></>, href);
  }

  if (refKind === "subtype" || (!refKind && subTypeVersionRef)) {
    if (!subTypeVersionRef) return <em>subtype (unset)</em>;
    const split = splitVersion(subTypeVersionRef);
    const href = split
      ? `/w/${split.name}/v/${split.version}`
      : `/w/${subTypeVersionRef}`;
    return wrap(
      <>{subTypeVersionRef} <span className="ref-kind">subtype</span></>,
      href,
    );
  }

  if (refKind === "helper" || (!refKind && helperRef)) {
    if (!helperRef) return <em>helper (unset)</em>;
    return wrap(<>{helperRef} <span className="ref-kind">helper</span></>, `/helpers/${helperRef}`);
  }

  // primitive
  const label = primitiveType ?? "any";
  return (
    <span className="ref ref-primitive">
      <code>{label}</code>
      {isList && <span className="ref-list">[]</span>}
      <span className="ref-kind">primitive</span>
    </span>
  );
}
