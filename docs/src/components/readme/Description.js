import React, {Component} from 'react';
import CodeFactorBadge from '../badge/CodeFactorBadge';
import PyPiBadge from '../badge/PyPiBadge';
import SourceBadge from '../badge/SourceBadge';
import TestBadge from '../badge/TestBadge';
import PythonVersionBadge from '../badge/PythonVersionBadge';

/**
* Component for project description
*/
export default class Description extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className='description'>
        <h1 className="mume-header" id="py-clash-bot">py-clash-bot</h1>
        <h2>
          <SourceBadge />
          <PythonVersionBadge/>
          <PyPiBadge />
          <TestBadge />
          <CodeFactorBadge />
        </h2>
        <p>A Clash Royale automation bot written in Python.</p>
      </div>
    );
  }
}
