const { BrowserWindow, shell } = require("electron");
const { ipcMain } = require("electron");

function initIpcListeners(mainWindow) {
  // listen for renderer process to minimize, close, and resize the window
  ipcMain.on("minimize-window", () => {
    mainWindow.minimize();
  });
  ipcMain.on("close-window", () => {
    mainWindow.close();
  });
  ipcMain.on("set-window-size", (event, width, height) => {
    let browserWindow = BrowserWindow.fromWebContents(event.sender);
    browserWindow.setSize(width, height);
  });
  // handle opening links externally
  ipcMain.on("new-window", (event, url) => {
    event.preventDefault();
    shell.openExternal(url);
  });
}

exports.initIpcListeners = initIpcListeners;
