import React from "react";

function BoxFrame(props) {
  const boxFrameStyle = {
    border: "1px solid #000000",
    backgroundColor: "#C0C0C0",
    padding: "5px",
    margin: "5px 2px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    alignItems: "stretch",
    height: "100%",
  };

  const boxFrameTitleStyle = {
    fontSize: "14px",
    margin: "-14px 0px 0px 0px",
    padding: "0px 5px",
    backgroundColor: "#C0C0C0",
    position: "absolute",
  };

  const boxFrameContentStyle = {
    flex: 1,
    flexGrow: 1,
    overflow: "auto",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    marginTop: "3px",
  };

  return (
    <div style={boxFrameStyle}>
      <div style={boxFrameTitleStyle}>{props.title}</div>
      <div style={boxFrameContentStyle}>{props.children}</div>
    </div>
  );
}

export default BoxFrame;
