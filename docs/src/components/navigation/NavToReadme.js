import React, { Component } from "react";
import { Link } from "react-router-dom";

/**
 * Component for NavToReadme
 */
export default class NavToReadme extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="nav">
        <Link to="/">Back to home</Link>
      </div>
    );
  }
}
