import React, {Component} from 'react';

/**
* Component for configuration instructions
*/
export default class Configuration extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className='configuration'>
        <h2 className="mume-header" id="install">Configuration</h2>
        <p>
            To configure the program, edit &nbsp;
          <code>config.json</code>
            &nbsp; in the install location of the program.
        </p>
      </div>
    );
  }
}
