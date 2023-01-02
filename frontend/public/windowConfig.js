const path = require("path");

module.exports = {
  window: {
    width: 480,
    height: 600,
    icon: path.join(__dirname, "../src/assets/icon.ico"),
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
  },
};
