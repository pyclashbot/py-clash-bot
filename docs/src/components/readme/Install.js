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
        <ReleaseLink />
        <p><ReleaseUpdate />
        with <ReleaseDownloadCount /> downloads.</p>
      </div>
    );
  }
}
