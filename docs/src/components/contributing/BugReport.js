import React, {Component} from 'react';
import {bugReportEvent, featureRequestEvent} from '../../GoogleAnalytics';

/**
 * Component for bug report
 */
export default class BugReport extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="dependencies">
        <h2>Bug Report and Feature Request</h2>
        <p>
          Open a bug report{' '}
          <a
            href="https://github.com/matthewmiglio/py-clash-bot/issues/new?template=bug_report.md"
            rel="nofollow"
            onClick={() => bugReportEvent()}
          >
            here
          </a>
          . Open a feature request{' '}
          <a
            href="https://github.com/matthewmiglio/py-clash-bot/issues/new?template=feature_request.md"
            rel="nofollow"
            onClick={() => featureRequestEvent()}
          >
            here
          </a>
          .
        </p>
      </div>
    );
  }
}
