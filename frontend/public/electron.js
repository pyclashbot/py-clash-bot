const { app, BrowserWindow, protocol } = require("electron");
const path = require("path");
const url = require("url");
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
    : url.format({
        pathname: path.join(__dirname, "index.html"),
        protocol: "file:",
        slashes: true,
      });
  mainWindow.loadURL(startUrl);
  mainWindow.on("closed", function () {
    mainWindow = null;
  });
}

function setupLocalFilesNormalizerProxy() {
  protocol.registerHttpProtocol(
    "file",
    (request, callback) => {
      const url = request.url.slice(8);
      callback({ path: path.normalize(`${__dirname}/${url}`) });
    },
    (error) => {
      if (error) console.error("Failed to register protocol");
    }
  );
}

app.disableHardwareAcceleration()
app.commandLine.appendSwitch("lang", "en-US");

app.on("ready", () => {
  createWindow();
  setupLocalFilesNormalizerProxy();
  initIpcListeners(mainWindow);
  if (!isDev) exeProcess = startBackend();
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
  stopBackend(exeProcess);
});
