import React, {Component} from 'react';
import {handleClick} from '../../GoogleAnalytics';
import './Badge.css';

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
      <h1 className='badge-flex'>
        <a className='badge' href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-build-msi.yml" onClick={handleClick}>
          <img
            alt="Build windows package"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-build-msi.yml/badge.svg"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
        <a className='badge' href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml" onClick={handleClick}>
          <img
            alt="GitHub Python Tests"
            src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml/badge.svg"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
        <a className='badge' href="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot" onClick={handleClick}>
          <img
            alt="CodeFactor"
            src="https://www.codefactor.io/repository/github/matthewmiglio/py-clash-bot/badge"
            content="no-cache, no-store, must-revalidate"
          />
        </a>
      </h1>
    );
  }
}
