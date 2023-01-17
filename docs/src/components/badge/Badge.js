import React, { Component } from "react";
import { handleClick } from "../../GoogleAnalytics";

/**
 *A component for all the badges
 */
export default class Badge extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <h2 style={{ display: "flex", flexWrap: "wrap", justifyContent: "left" }}>
        <a
          style={{ marginRight: "6px" }}
          href="hhttps://github.com/matthewmiglio/py-clash-bot/actions/workflows/build-and-package.yaml"
          onClick={handleClick}
        >
          <img
            alt="Build windows package"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-build-msi.yml/badge.svg"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
        <a
          style={{ marginRight: "6px" }}
          href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml"
          onClick={handleClick}
        >
          <img
            alt="GitHub Python Tests"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml/badge.svg"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
        <a
          style={{ marginRight: "6px" }}
          href="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot"
          onClick={handleClick}
        >
          <img
            alt="CodeFactor"
            src="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot/badge"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
      </h2>
    );
  }
}
