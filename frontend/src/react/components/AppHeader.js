import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faMinus,
  faTimes,
  faQuestion,
} from "@fortawesome/free-solid-svg-icons";
import React from "react";
import logo from "../../assets/icon.png";
const { ipcRenderer } = window.require("electron");

const Header = () => {
  const blockStyles = {
    marginTop: 0,
    marginBottom: 0,
    padding: 2,
    backgroundColor: "#C0C0C0",
    boxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
    WebkitBoxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
    MozBoxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
  };

  const headerStyles = {
    width: "100%",
    display: "flex",
    backgroundColor: "#018281",
    color: "#FFFFFF",
    boxShadow: "inset -1px -2px 0px #FFFFFF, inset 2px 2px 0px #000000",
    WebkitBoxShadow: "inset -1px -2px 0px #FFFFFF, inset 2px 2px 0px #000000",
    MozBoxShadow: "inset -1px -2px 0px #FFFFFF, inset 2px 2px 0px #000000",
    height: "28px",
    alignItems: "center",
  };

  const handleMinimize = () => {
    ipcRenderer.send("minimize-window");
  };

  const handleClose = () => {
    ipcRenderer.send("close-window");
  };

  const handleHelp = () => {
    ipcRenderer.send(
      "new-window",
      "https://matthewmiglio.github.io/py-clash-bot/?utm_source=help_button&utm_medium=app"
    );
  };

  return (
    <div style={blockStyles}>
      <div style={headerStyles}>
        <div
          style={{
            paddingLeft: "3px",
            WebkitAppRegion: "drag",
            flexGrow: 1,
            userSelect: "none",
          }}
        >
          <div style={{ display: "flex", alignItems: "center" }}>
            <img src={logo} alt="logo" style={{ height: "21px" }} />
            <div style={{ paddingLeft: "3px" }}>py-clash-bot</div>
          </div>
        </div>
        <div style={{ marginRight: "5px" }}>
          <button onClick={handleHelp}>
            <FontAwesomeIcon icon={faQuestion} />
          </button>
          <button onClick={handleMinimize}>
            <FontAwesomeIcon icon={faMinus} />
          </button>
          <button onClick={handleClose}>
            <FontAwesomeIcon icon={faTimes} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header;
