const path = require("path");
const isDev = require("electron-is-dev");
const { spawn } = require("child_process");

// a function to start the backend process
function startBackend() {
  const exeName = "pycb_back.exe";
  let exeProc = spawn(
    path.join(
      __dirname,
      isDev ? "../../backend/build/exe.win-amd64-3.11" : "../../../../bin/",
      exeName
    )
  );

  // setup listeners for the backend process to log stdout and stderr
  const consoleOutput = (data) => {
    console.log(`[BACKEND]: ${data}`);
  };
  exeProc.stdout.on("data", consoleOutput);
  exeProc.stderr.on("data", consoleOutput);
  return exeProc;
}
exports.startBackend = startBackend;
// a function to stop the backend process
function stopBackend(exeProcess) {
  if (exeProcess) exeProcess.kill();
}
exports.stopBackend = stopBackend;
