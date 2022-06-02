import Dependencies from './components/readme/Dependencies';
import Description from './components/readme/Description';
import Execution from './components/readme/Execution';
import Install from './components/readme/Install';
import {initializeGA} from './GoogleAnalytics';
import React from 'react';

/**
 * main app
 * @return {Component} App
 */
export default function App() {
  initializeGA();
  return (
    <div className="mume markdown-preview  ">
      <Description/>
      <Install/>
      <Dependencies/>
      <Execution/>
    </div>
  );
}
