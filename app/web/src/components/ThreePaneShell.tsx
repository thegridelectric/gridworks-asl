import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

export function ThreePaneShell() {
  const loc = useLocation();
  return (
    <div className="shell">
      <header className="topbar">
        <span className="brand">
          <Link to="/">sema · Registry Explorer</Link>
        </span>
        <span className="breadcrumb">{loc.pathname}</span>
      </header>
      <div className="three-pane">
        <nav className="pane">
          <h2>Navigate</h2>
          <ul className="nav">
            <li>
              <NavLink to="/" end>
                Workbench
              </NavLink>
            </li>
            <li>
              <NavLink to="/search">Search</NavLink>
            </li>
          </ul>
          <h2>Vocabularies</h2>
          <ul className="nav" id="vocab-nav">
            <li>
              <NavLink to="/v/gridworks-energy">gridworks-energy</NavLink>
            </li>
            <li>
              <NavLink to="/v/jessica-millar">jessica-millar</NavLink>
            </li>
            <li>
              <NavLink to="/v/joe-strommen">joe-strommen</NavLink>
            </li>
            <li>
              <NavLink to="/v/microerapower">microerapower</NavLink>
            </li>
            <li>
              <NavLink to="/v/smoothstone-computing">smoothstone-computing</NavLink>
            </li>
            <li>
              <NavLink to="/v/thomas-defauw">thomas-defauw</NavLink>
            </li>
          </ul>
          <h2>Axes</h2>
          <ul className="nav">
            <li>
              <NavLink to="/activity">Activity</NavLink>
            </li>
          </ul>
        </nav>
        <Outlet />
      </div>
    </div>
  );
}
