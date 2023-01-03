import React, { useState } from "react";

import AccountDropDown from "./AccountDropDown";
import JobDropDown from "./JobDropDown";

function Controls({
  startThread,
  stopThread,
  pauseThreadToggle,
  threadStarted,
  threadPaused,
}) {
  const [selectedJobs, setJobs] = useState(null);
  const [selectedAccounts, setAccounts] = useState(null);
  return (
    <>
      <div
        style={{
          width: "auto",
          height: "100%",
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <div style={{ minWidth: "135px", marginRight: "5px" }}>
          <AccountDropDown
            selectedOptions={selectedAccounts}
            onChange={setAccounts}
          />
        </div>
        <button
          onClick={() =>
            startThread(
              selectedJobs.map((job) => job.value),
              selectedAccounts.value
            )
          }
          disabled={threadStarted}
          style={{ flexGrow: 1 }}
        >
          Start
        </button>
        <button
          onClick={pauseThreadToggle}
          disabled={!threadStarted}
          style={{ flexGrow: 1 }}
        >
          {!threadPaused ? "Pause" : "Resume"}
        </button>
        <button
          onClick={stopThread}
          disabled={!threadStarted}
          style={{ flexGrow: 1 }}
        >
          Stop
        </button>
      </div>
      <div style={{ marginTop: "5px" }}>
        <JobDropDown selectedOptions={selectedJobs} onChange={setJobs} />
      </div>
    </>
  );
}

export default Controls;
