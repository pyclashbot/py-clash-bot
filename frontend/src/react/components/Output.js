import React from "react";

import ThreadTimer from "./ThreadTimer";

function Output({ threadStarted, output }) {
  return (
    <div style={{ margin: "3px 0 0 0", display: "flex" }}>
      <ThreadTimer isActive={threadStarted} />
      <input
        value={output ?? "Idle"}
        readOnly
        style={{
          flexGrow: 1,
          boxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
          WebkitBoxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
          MozBoxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
        }}
      />
    </div>
  );
}

export default Output;
