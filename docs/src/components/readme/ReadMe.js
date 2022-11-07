import MEmuDependency from "./MEmuDependency";
import Description from "./Description";
import Execution from "./Execution";
import Install from "./Install";
import React, { Component } from "react";
import NavToContributing from "../navigation/NavToContributing";

/**
 * Component for project description
 */
export default class ReadMe extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="mume markdown-preview  ">
        <Description />
        <Install />
        <MEmuDependency />
        <Execution />
        <NavToContributing />
      </div>
    );
  }
}
