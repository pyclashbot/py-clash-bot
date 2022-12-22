const { BrowserWindow, shell } = require("electron");
const { ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");

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

  //listener to save user settings to a file in appdata
  ipcMain.on("save-settings", (event, settings) => {
    fs.writeFileSync(
      path.join(process.env.APPDATA, "py-clash-bot", "settings.json"),
      JSON.stringify(settings)
    );
  });

  //listener to load user settings from a file in appdata
  ipcMain.on("load-settings", (event) => {
    try {
      let settings = fs.readFileSync(
        path.join(process.env.APPDATA, "py-clash-bot", "settings.json")
      );
      event.returnValue = JSON.parse(settings);
    } catch (err) {
      // no settings file found, return null
      event.returnValue = null;
    }
  });
}

exports.initIpcListeners = initIpcListeners;
