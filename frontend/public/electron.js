const { app, BrowserWindow } = require("electron");
const path = require("path");
const isDev = require("electron-is-dev");
const { initIpcListeners } = require("./ipcListeners");
const { startBackend, stopBackend } = require("./backendLinker");

let mainWindow;
let exeProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 480,
    height: 600,
    icon: path.join(__dirname, "../src/assets/icon.ico"),
    show: false,
    frame: false,
    transparent: true,
    //resizable: false, //when true, the window will auto shrink, when false, the window cant be resized by user
    autoHideMenuBar: true,
    webPreferences: {
      allowFileAccessFromFileUrls: true,
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });
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
