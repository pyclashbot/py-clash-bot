const { app, BrowserWindow } = require("electron");
const path = require("path");
const isDev = require("electron-is-dev");
const { initIpcListeners } = require("./ipcListeners");
const { startBackend, stopBackend } = require("./backendLinker");
const windowConfig = require("./windowConfig");

let mainWindow;
let exeProcess;

function createWindow() {
  mainWindow = new BrowserWindow(windowConfig.window);
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: "undocked" });
  }
  const startUrl = isDev
    ? "http://localhost:3000"
    : `file:${path.join(__dirname, "../index.html")}`;
  mainWindow.loadURL(startUrl);
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });
  mainWindow.on("closed", function () {
    mainWindow = null;
  });
}

app.commandLine.appendSwitch("lang", "en-US");

app.whenReady().then(() => {
  if (!isDev) exeProcess = startBackend();
  createWindow();
  initIpcListeners(mainWindow);
  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
  stopBackend(exeProcess);
});
