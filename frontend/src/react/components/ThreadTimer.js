import React, { useState, useEffect } from "react";

function ThreadTimer({ isActive }) {
  const [time, setTime] = useState(0);

  useEffect(() => {
    let interval = null;
    console.log("Timer effected");
    if (isActive) {
      interval = setInterval(() => {
        setTime((time) => time + 100);
        console.log("Timer ticked");
      }, 100);
    } else {
      clearInterval(interval);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isActive]);

  return (
    <input
      type="text"
      value={new Date(time).toISOString().slice(11, -5)}
      readOnly
      style={{
        width: 52,
        textAlign: "right",
        boxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
        WebkitBoxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
        MozBoxShadow: "-1px -1px 0px #5f5f5f, 1px 1px 0px #FFFFFF",
      }}
    />
  );
}

export default ThreadTimer;
