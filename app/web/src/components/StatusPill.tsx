type Status = "draft" | "active" | "deprecated" | "retired" | string | null | undefined;

export function StatusPill({
  status,
  retired,
}: {
  status: Status;
  retired?: boolean;
}) {
  if (retired) return <span className="pill retired">retired</span>;
  if (!status) return null;
  const cls =
    status === "draft" || status === "active" || status === "deprecated"
      ? `pill ${status}`
      : "pill";
  return <span className={cls}>{status}</span>;
}
