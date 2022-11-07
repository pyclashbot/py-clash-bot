import React, {Component} from 'react';
import memuAppearanceSettings from '../../assets/memu_appearance_settings.webp';
import memuDisplaySettings from '../../assets/memu_display_settings.webp';
import memuInstaceSettings from '../../assets/memu_instance_settings.webp';
import {memuDownloadEvent} from '../../GoogleAnalytics';

/**
 * Component for memu dependency instructions
 */
export default class MEmuDependency extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="dependencies">
        <h2>MEmu Dependency</h2>
        <p>
          To emulate the game,{' '}
          <a
            href="https://www.memuplay.com/"
            rel="nofollow"
            onClick={() => memuDownloadEvent()}
          >
            Download and install MEmu
          </a>
          .
        </p>
        <h3>Configure MEmu</h3>
        <p>
          Using the Multiple Instance Manager, set the instance, display, and
          appearance settings of your instance to match the following
        </p>
        <p>
          <img
            src={memuInstaceSettings}
            alt="MEmu instace options"
            style={{mixBlendMode: 'lighten'}}
            content="no-cache, no-store, must-revalidate"
            height={memuAppearanceSettings.height}
            width={memuAppearanceSettings.width}
          />
        </p>
        <p>
          <img
            src={memuDisplaySettings}
            alt="MEmu display options"
            style={{mixBlendMode: 'lighten'}}
            content="no-cache, no-store, must-revalidate"
            height={memuDisplaySettings.height}
            width={memuDisplaySettings.width}
          />
        </p>
        <p>
          <img
            src={memuAppearanceSettings}
            alt="MEmu appearance options"
            style={{mixBlendMode: 'lighten'}}
            content="no-cache, no-store, must-revalidate"
            height={memuAppearanceSettings.height}
            width={memuAppearanceSettings.width}
          />
        </p>
        <p>
          Then start the emulator and install Clash Royale with the Google Play
          Store.
        </p>
      </div>
    );
  }
}
