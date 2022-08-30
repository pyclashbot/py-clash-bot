import React, {Component} from 'react';
import {pythonVersionBadgeEvent} from '../../GoogleAnalytics';

/**
* Component for latest release download link
*/
export default class PythonVersionBadge extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <a href="https://www.python.org/downloads/" rel="nofollow" onClick={() => pythonVersionBadgeEvent()}>
        <img
          src="https://img.shields.io/pypi/pyversions/py-clash-bot"
          alt="Python version"
          style={{marginRight: '3px'}}
          content="no-cache, no-store, must-revalidate"
          rel="preconnect"
          height="20"
          width="84"
        />
      </a>
    );
  }
}
