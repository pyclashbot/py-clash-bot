// <a href="https://badge.fury.io/py/py-clash-bot"><img src="https://badge.fury.io/py/py-clash-bot.svg" alt="PyPI version" height="18"></a>

import React, {Component} from 'react';
import {pypiBadgeEvent} from '../../GoogleAnalytics';

/**
* Component for latest release download link
*/
export default class PyPiBadge extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <a href="https://pypi.org/project/py-clash-bot/" rel="nofollow" onClick={() => pypiBadgeEvent()}>
        <img
          src="https://badge.fury.io/py/py-clash-bot.svg"
          alt="PyPI version"
          style={{marginRight: '3px'}}
        />
      </a>
    );
  }
}
