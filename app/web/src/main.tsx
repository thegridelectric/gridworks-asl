import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { LoginGate } from "./components/LoginGate";
import { installAuthFetchInterceptor } from "./lib/auth";
import { router } from "./router";
import "./styles.css";

installAuthFetchInterceptor();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <LoginGate>
      <RouterProvider router={router} />
    </LoginGate>
  </React.StrictMode>,
);
