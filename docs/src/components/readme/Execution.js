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
        <p>
          Before attempting to run the bot, make sure both the &#39;Multi
          Instance Manager&#39; and the MEmu client are both open.
        </p>
        <h4>a. Installed on Windows</h4>
        <p>Run the desktop shortcut the installer created.</p>
        <h4>b. Installed with pip</h4>
        <p>Enter <code>pyclashbot</code> in the command line.</p>
      </div>
    );
  }
}
