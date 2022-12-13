/* eslint-disable max-len */
import React, {Component} from 'react';
import {handleClick} from '../../GoogleAnalytics';
import ReleaseLink from '../release/ReleaseLink';
import Badge from '../badge/Badge';
import logo from '../../assets/pixel-pycb.svg';
import demogame from '../../assets/demo-game.webp';
import demogui from '../../assets/demo-gui.webp';
import './ReadMe.css';

/**
 * Component for project description
 */
export default class ReadMe extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="ReadMe">
        <div className='block'>
          <div className='header-block'>
            <div className='text-block'>
              <h1>py-clash-bot</h1>
              <Badge/>
            </div>
            <div className='logo-block'>
              <img className='logo' alt="py-clash-bot logo" src={logo}
                content="max-age=259200" />
            </div>
          </div>
          <p className='description'>
                py-clash-bot is an open-source application that allows users to automate
                their Clash Royale gameplay on Windows using an emulated Android phone. The
                bot uses a combination of image recognition, mouse control, and Android
                emulation to perform a variety of tasks without user intervention.
          </p>
        </div>
        <div className='block'>
          <h2>Features</h2>
          <ul>
            <li>Automated level-up, clan wars and donations</li>
            <li>Automatic chest farming</li>
            <li>Multi-account support</li>
          </ul>
        </div>
        <div className='block'>
          <h2>Installation</h2>
          <ol>
            <li>
              <ReleaseLink child={<button className='download-button'>Download</button>} /> and run the latest windows installer
            </li>
            <li>Run the shortcut on the desktop</li>
            <li>
            The program will automatically install MEmu and AutoHotKey, follow the
            installation prompts
            </li>
          </ol>
        </div>
        <div className='block'>
          <h2>Usage</h2>
          <ol>
            <li>Configure the jobs to perform, and number of accounts</li>
            <li>
            Click the <code>Start</code> button to begin automation
            </li>
            <li>
            Enjoy the benefits of always-on farming with the py-clash-bot taking care
            of the heavy lifting for you
            </li>
          </ol>
        </div>
        <div className='block'>
          <h2>Demo</h2>
          <div className="demo">
            <img className='demo-game' alt="Clash Royale gameplay" src={demogame}/>
            <img className='demo-gui' alt="User interface" src={demogui} />
          </div>
        </div>
        <div className='block'>
          <h2>Contribute</h2>
          <p>
          We welcome contributions to the py-clash-bot project. If you have an idea for a
          new feature or have found a bug, please open an issue on the{' '}
            <a href="https://github.com/matthewmiglio/py-clash-bot/issues" onClick={handleClick}>issues tab</a>{' '}
          or submit a pull request.
          </p>
          <p>The source code can be viewed on{' '}
            <a href="https://github.com/matthewmiglio/py-clash-bot" onClick={handleClick}>GitHub</a>.
          </p>
        </div>
      </div >
    );
  }
}
