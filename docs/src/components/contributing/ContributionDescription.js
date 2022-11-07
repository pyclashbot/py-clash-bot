import React, { Component } from "react";
import CodeFactorBadge from "../badge/CodeFactorBadge";
import SourceBadge from "../badge/SourceBadge";
import TestBadge from "../badge/TestBadge";

/**
 * Component for Contribution description
 */
export default class ContributionDescription extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="description">
        <h1 className="mume-header" id="py-clash-bot">
          Contributing
        </h1>
        <h2>
          <SourceBadge />
          <TestBadge />
          <CodeFactorBadge />
        </h2>
        <p>
          To contribute to this project, either open a bug report, a feature
          request or a pull request
        </p>
      </div>
    );
  }
}
