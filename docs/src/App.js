import ReadMe from './components/readme/ReadMe';
import {initializeGA} from './GoogleAnalytics';
import React from 'react';
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import AppHelmet from './components/AppHelmet';
import './App.css';

/**
 * main app
 * @return {Component} App
 */
export default function App() {
  initializeGA();
  return (
    <Router basename="/py-clash-bot">
      <div className="App">
        <AppHelmet />
        <Routes>
          <Route path="/" element={<ReadMe />} />
        </Routes>
      </div>
    </Router>
  );
}
