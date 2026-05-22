import { Link, Outlet } from "react-router-dom";

/**
 * AdminShell — top bar + outlet. Admin gets its own layout (no three-pane
 * vocab nav) because the drift inspector wants the full screen width for
 * its YAML tree + diff + tool runner columns.
 */
export function AdminShell() {
  return (
    <div className="admin-shell-root">
      <header className="topbar">
        <span className="brand">
          <Link to="/">sema · Registry Explorer</Link>
        </span>
        <span className="breadcrumb">/admin · YAML ⇄ rulebook inspector</span>
      </header>
      <Outlet />
    </div>
  );
}
