import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./react/App";
const { ipcRenderer } = window.require("electron");

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// track page changes to resize the window to fit the content
new MutationObserver((mutations) => {
  ipcRenderer.send(
    "set-window-size",
    480,
    document.documentElement.offsetHeight
  );
}).observe(document.body, {
  attributes: true,
  childList: true,
  subtree: true,
});
