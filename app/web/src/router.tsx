import { createBrowserRouter } from "react-router-dom";
import { ThreePaneShell } from "./components/ThreePaneShell";
import { Placeholder } from "./components/Placeholder";
import { Workbench } from "./routes/Workbench";
import { OwnerView } from "./routes/Owner";
import { WordView } from "./routes/Word";
import { TypeVersionView } from "./routes/TypeVersion";
import { EnumView, EnumVersionView } from "./routes/Enum";
import { FormatView } from "./routes/Format";
import { HelperView } from "./routes/Helper";
import { ProjectionView } from "./routes/Projection";
import { SearchView } from "./routes/Search";
import { AdminView } from "./routes/Admin";
import { AdminShell } from "./components/AdminShell";
import {
  EnumUpgradeChainView,
  EnumUpgradeEdgeView,
  TypeUpgradeChainView,
  TypeUpgradeEdgeView,
} from "./routes/Upgrades";
import {
  VocabEnumsView,
  VocabFormatsView,
  VocabWordsView,
} from "./routes/VocabularyTabs";

/**
 * URL skeleton for APP_PLAN §8. Phase 3 brings every read-only route online.
 * Edit / fork / diff / promote routes (§5 steps 7–9) remain placeholders for
 * Phases 5–7.
 */
export const router = createBrowserRouter([
  {
    path: "/",
    element: <ThreePaneShell />,
    children: [
      { index: true, element: <Workbench /> },
      { path: "search", element: <SearchView /> },
      { path: "activity", element: <Placeholder phase="Phase 4" title="Activity" /> },

      { path: "v/:owner", element: <OwnerView /> },
      { path: "v/:owner/words", element: <VocabWordsView /> },
      { path: "v/:owner/enums", element: <VocabEnumsView /> },
      { path: "v/:owner/formats", element: <VocabFormatsView /> },
      { path: "owners/:owner", element: <OwnerView /> },

      { path: "w/:typeName", element: <WordView /> },
      { path: "w/:typeName/v/:version", element: <TypeVersionView /> },
      { path: "w/:typeName/v/:version/edit", element: <Placeholder phase="Phase 5" title="Definition — edit mode" /> },
      { path: "w/:typeName/v/:version/diff/:other", element: <Placeholder phase="Phase 7" title="Definition — diff" /> },
      { path: "w/:typeName/fork-from/:version", element: <Placeholder phase="Phase 6" title="Fork action" /> },

      { path: "enums/:name", element: <EnumView /> },
      { path: "enums/:name/v/:version", element: <EnumVersionView /> },
      { path: "enums/:name/v/:version/edit", element: <Placeholder phase="Phase 5" title="Enum version — edit" /> },
      { path: "enums/:name/fork-from/:version", element: <Placeholder phase="Phase 6" title="Enum fork action" /> },

      { path: "formats/:name", element: <FormatView /> },
      { path: "formats/:name/edit", element: <Placeholder phase="Phase 5" title="Format — edit" /> },
      { path: "formats/:name/replace", element: <Placeholder phase="Phase 6" title="Format successor" /> },

      { path: "projections/:name", element: <ProjectionView /> },
      { path: "projections/new", element: <Placeholder phase="Phase 6" title="New projection" /> },

      { path: "type-upgrades", element: <TypeUpgradeChainView /> },
      { path: "type-upgrades/:name", element: <TypeUpgradeChainView /> },
      { path: "type-upgrades/:word/:fromVersion-to-:toVersion", element: <TypeUpgradeEdgeView /> },

      { path: "enum-upgrades", element: <EnumUpgradeChainView /> },
      { path: "enum-upgrades/:name", element: <EnumUpgradeChainView /> },
      { path: "enum-upgrades/:word/:fromVersion-to-:toVersion", element: <EnumUpgradeEdgeView /> },

      { path: "helpers/:name", element: <HelperView /> },

      { path: "*", element: <Placeholder phase="(404)" title="Not Found" /> },
    ],
  },
  {
    path: "/admin",
    element: <AdminShell />,
    children: [
      { index: true, element: <AdminView /> },
    ],
  },
]);
