import React, { Component } from "react";

/**
 * Component for Execution instructions
 */
export default class Execution extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="execution">
        <h2>Run py-clash-bot on Windows</h2>
        <p>Run the desktop shortcut the installer created.</p>
      </div>
    );
  }
}
