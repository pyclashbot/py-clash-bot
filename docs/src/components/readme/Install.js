import React, {Component} from 'react';
import ReleaseDownloadCount from '../release/ReleaseDownloadCount';
import ReleaseLink from '../release/ReleaseLink';
import ReleaseUpdate from '../release/ReleaseUpdate';

/**
* Component for install instructions
*/
export default class Install extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className='install'>
        <h2 className="mume-header" id="install">Install</h2>
        <p>Choose one of the install methods below.</p>
        <h4 className="mume-header" id="a-windows-install">
            a. Windows Install
        </h4>
        <ReleaseLink />
        <p><ReleaseUpdate />
        with <ReleaseDownloadCount /> downloads.</p>
        <h4 className="mume-header" id="b-install-from-source">
        b. Install with pip
        </h4>
        <p>Enter the following into the command line:</p>
        <code>pip install py-clash-bot</code>
      </div>
    );
  }
}
