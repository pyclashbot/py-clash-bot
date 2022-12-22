import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./react/App";
import reportWebVitals from "./reportWebVitals";
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

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
