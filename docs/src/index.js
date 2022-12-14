import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';
import {initializeGA} from './GoogleAnalytics';
import './index.css';

initializeGA();

const root = createRoot(document.getElementById('root'));
root.render(<App />);

reportWebVitals();
