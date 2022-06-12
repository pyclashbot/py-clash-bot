import React, {Component} from 'react';

/**
* Component for developer install instructions
*/
export default class DevInstall extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className='dev-install'>
        <h2 className="mume-header" id="dev-install">Developer Install</h2>
        <p>
        To contribute directly, follow the instructions
        to install for development.
        </p>
        <p>Clone repository and enter directory
          <p><code>git clone https://github.com/matthewmiglio/py-clash-bot.git</code></p>
          <p><code>cd py-clash-bot</code></p>
        </p>
        <p>Prepare your python environment
          <p><code>python -m venv .venv</code></p>
          Activate venv for Linux/Unix
          <p><code>./.venv/Scripts/activate</code></p>
          or for Windows
          <p><code>./.venv/Scripts/Activate.ps1
          </code></p>
        </p>
        <p>Install repository development dependencies and scripts
          <p><code>pip install -r ./requirements.txt</code></p>
          <p><code>pip install -e .
          </code></p>
        </p>
      </div>
    );
  }
}
