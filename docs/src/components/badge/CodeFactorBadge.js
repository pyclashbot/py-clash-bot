// <a href="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot"><img src="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot/badge" alt="CodeFactor" /></a>

import React, {Component} from 'react';
import {codeFactorBadgeEvent} from '../../GoogleAnalytics';

/**
* Component for latest release download link
*/
export default class CodeFactorBadge extends Component {
  /**
     * react render override
     * @return {JSX.Element}
     */
  render() {
    return (
      <a href="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot" rel="nofollow" onClick={() => codeFactorBadgeEvent()}>
        <img
          src="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot/badge"
          alt="CodeFactor badge"
        />
      </a>
    );
  }
}
