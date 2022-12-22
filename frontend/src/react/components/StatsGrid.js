import React from "react";
import { splitList } from "../functions/lists";
import { v4 as uuidv4 } from "uuid";

const fontSize = "11.6px";

const StatsGrid = ({ stats, columnCount }) => {
  const columns = splitList(stats, columnCount);

  return (
    <div
      className="container"
      style={{
        display: "flex",
      }}
    >
      {columns.map((column, index) => (
        <div
          key={uuidv4()}
          className="column"
          style={{
            display: "flex",
          }}
        >
          <div className="title-column">
            {column.map((item) => (
              <div
                key={item.title}
                className="title-item"
                style={{
                  textAlign: "right",
                  margin: "1px 1px",
                  padding: "0px 5px",
                  fontSize: fontSize,
                }}
              >
                {item.title}
              </div>
            ))}
          </div>
          <div className="value-column">
            {column.map((item) => (
              <div
                key={item.value}
                className="value-item"
                style={{
                  width: "15px",
                  textAlign: "left",
                  margin: "1px 0px 1px 1px",
                  padding: "0px 5px",
                  fontSize: fontSize,
                  background: "white",
                  color: "#018281",
                  boxShadow:
                    "inset -1px -1px 0px #FFFFFF, inset 1px 1px 0px #000000",
                  WebkitBoxShadow:
                    "inset -1px -1px 0px #FFFFFF, inset 1px 1px 0px #000000",
                  MozBoxShadow:
                    "inset -1px -1px 0px #FFFFFF, inset 1px 1px 0px #000000",

                }}
              >
                {item.value}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatsGrid;
