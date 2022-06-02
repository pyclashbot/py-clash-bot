import React, {Component} from 'react';

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
      <div className='execution'>
        <h2>Run py-clash-bot</h2>
        <h4>a. Installed on Windows</h4>
        <p>Run the d;esktop shortcut the installer created.</p>
        <h4>b. Installed with pip</h4>
        <p>Enter <code>pyclashbot</code> in the command line.</p>
      </div>
    );
  }
}
