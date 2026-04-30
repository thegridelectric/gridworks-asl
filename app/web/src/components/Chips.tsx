/**
 * Read-only calc-field chips per APP_PLAN §10. Used as live feedback
 * around detail headers (and later, around forms in Phase 5).
 */

export function Chip({
  label,
  value,
  tone,
  title,
}: {
  label: string;
  value?: string | number | null;
  tone?: "default" | "warn" | "danger" | "ok";
  title?: string;
}) {
  const cls = tone && tone !== "default" ? `chip chip-${tone}` : "chip";
  return (
    <span className={cls} title={title}>
      <span className="chip-label">{label}</span>
      {value !== undefined && value !== null && <span className="chip-value">{String(value)}</span>}
    </span>
  );
}

export function ChipRow({ children }: { children: React.ReactNode }) {
  return <div className="chip-row">{children}</div>;
}

export function BoolChip({
  label,
  value,
  trueTone = "ok",
  falseTone,
  title,
}: {
  label: string;
  value: boolean | null | undefined;
  trueTone?: "ok" | "warn" | "danger" | "default";
  falseTone?: "ok" | "warn" | "danger" | "default";
  title?: string;
}) {
  if (value === null || value === undefined) return null;
  const tone = value ? trueTone : (falseTone ?? "default");
  return <Chip label={label} value={value ? "yes" : "no"} tone={tone} title={title} />;
}
