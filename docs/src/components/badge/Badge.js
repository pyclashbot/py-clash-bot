import React, { Component } from "react";
import Image from "next/image";
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
          href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/build-and-package.yaml"
          onClick={handleClick}
        >
          <Image
            alt="Build windows package"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/build-and-package.yaml/badge.svg"
            content="no-cache, no-store, must-revalidate"
            height={20}
            width={206}
          />
        </a>
        <a
          style={{ marginRight: "6px" }}
          href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml"
          onClick={handleClick}
        >
          <Image
            alt="GitHub Python Tests"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml/badge.svg"
            content="no-cache, no-store, must-revalidate"
            height={20}
            width={142}
          />
        </a>
        <a
          style={{ marginRight: "6px" }}
          href="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot"
          onClick={handleClick}
        >
          <Image
            alt="CodeFactor Score"
            src="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot/badge"
            content="no-cache, no-store, must-revalidate"
            height={20}
            width={88}
          />
        </a>
      </h2>
    );
  }
}
