import React, {Component} from 'react';
import Helmet from 'react-helmet';

/**
* Component for app helmet
*/
export default class AppHelmet extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <Helmet>
        <meta charset="utf-8" />
        <title>py-clash-bot</title>
        <meta
          name="description"
          content="Automated Clash Royale"
        />
        <meta
          name="theme-color"
          content="#181d20"
        />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1.0"
        />
        <meta
          name="twitter:card"
          content="A Clash Royale automation bot written in Python"
        />
      </Helmet>
    );
  }
}


