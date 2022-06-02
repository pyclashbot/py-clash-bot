import React from 'react';
import './App.css';
import CodeFactorBadge from './components/badge/CodeFactorBadge';
import PyPiBadge from './components/badge/PyPiBadge';
import SourceBadge from './components/badge/SourceBadge';
import TestBadge from './components/badge/TestBadge';
import MEmuDependency from './components/instruction/MEmuDependency';
import ReleaseDownloadCount from './components/release/ReleaseDownloadCount';
import ReleaseLink from './components/release/ReleaseLink';
import ReleaseUpdate from './components/release/ReleaseUpdate';
import {initializeGA} from './GoogleAnalytics';

/**
 * main app
 * @return {Component} App
 */
export default function App() {
  initializeGA();
  return (
    <div className="mume markdown-preview  ">
      <h1 className="mume-header" id="py-clash-bot">py-clash-bot</h1>
      <h2>
        <SourceBadge />
        <PyPiBadge />
        <TestBadge />
        <CodeFactorBadge />
      </h2>
      <p>A Clash Royale automation bot written in Python.</p>
      <h2 className="mume-header" id="install">Install</h2>

      <p>Choose one of the install methods below.</p>
      <h4 className="mume-header" id="a-windows-install">a. Windows Install</h4>
      <ReleaseLink />
      <p><ReleaseUpdate />
        with <ReleaseDownloadCount /> downloads.</p>
      <h4 className="mume-header" id="b-install-from-source">
        b. Install with pip
      </h4>

      <p>Enter the following into the command line:</p>
      <code>pip install py-clash-bot</code>
      <MEmuDependency/>
      <h2>Run py-clash-bot</h2>
      <h4>a. Installed on Windows</h4>
      <p>Run the desktop shortcut the installer created.</p>
      <h4>b. Installed with pip</h4>
      <p>Enter <code>pyclashbot</code> in the command line.</p>

    </div>
  );
}
