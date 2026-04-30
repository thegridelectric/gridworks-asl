import { createBrowserRouter } from "react-router-dom";
import { ThreePaneShell } from "./components/ThreePaneShell";
import { Placeholder } from "./components/Placeholder";
import { Workbench } from "./routes/Workbench";
import { OwnerView } from "./routes/Owner";

/**
 * URL skeleton for APP_PLAN §8. Most routes are placeholders today;
 * the Workbench and Owner views are already wired to the typed API
 * client to prove the React → FastAPI → postgres path end-to-end.
 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <ThreePaneShell />,
    children: [
      { index: true, element: <Workbench /> },
      { path: "search", element: <Placeholder phase="Phase 3" title="Search" /> },
      { path: "activity", element: <Placeholder phase="Phase 4" title="Activity" /> },

      { path: "v/:owner", element: <OwnerView /> },
      { path: "v/:owner/words", element: <Placeholder phase="Phase 3" title="Words in vocabulary" /> },
      { path: "v/:owner/enums", element: <Placeholder phase="Phase 3" title="Enums in vocabulary" /> },
      { path: "v/:owner/formats", element: <Placeholder phase="Phase 3" title="Formats in vocabulary" /> },
      { path: "owners/:owner", element: <OwnerView /> },

      { path: "w/:typeName", element: <Placeholder phase="Phase 3" title="Word — version timeline" /> },
      { path: "w/:typeName/v/:version", element: <Placeholder phase="Phase 3" title="Definition — read mode" /> },
      { path: "w/:typeName/v/:version/edit", element: <Placeholder phase="Phase 5" title="Definition — edit mode" /> },
      { path: "w/:typeName/v/:version/diff/:other", element: <Placeholder phase="Phase 7" title="Definition — diff" /> },
      { path: "w/:typeName/fork-from/:version", element: <Placeholder phase="Phase 6" title="Fork action" /> },

      { path: "enums/:name", element: <Placeholder phase="Phase 3" title="Enum — version timeline" /> },
      { path: "enums/:name/v/:version", element: <Placeholder phase="Phase 3" title="Enum version — read mode" /> },
      { path: "enums/:name/v/:version/edit", element: <Placeholder phase="Phase 5" title="Enum version — edit" /> },
      { path: "enums/:name/fork-from/:version", element: <Placeholder phase="Phase 6" title="Enum fork action" /> },

      { path: "formats/:name", element: <Placeholder phase="Phase 3" title="Format — read mode" /> },
      { path: "formats/:name/edit", element: <Placeholder phase="Phase 5" title="Format — edit" /> },
      { path: "formats/:name/replace", element: <Placeholder phase="Phase 6" title="Format successor" /> },

      { path: "projections/:name", element: <Placeholder phase="Phase 3" title="Projection — read mode" /> },
      { path: "projections/new", element: <Placeholder phase="Phase 6" title="New projection" /> },

      { path: "type-upgrades/:name", element: <Placeholder phase="Phase 4" title="Type upgrade chain" /> },
      { path: "enum-upgrades/:name", element: <Placeholder phase="Phase 4" title="Enum upgrade chain" /> },
      { path: "helpers/:name", element: <Placeholder phase="Phase 3" title="Helper — read mode" /> },

      { path: "*", element: <Placeholder phase="(404)" title="Not Found" /> },
    ],
  },
]);
