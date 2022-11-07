import React, {Component} from 'react';
import {Link} from 'react-router-dom';

/**
 * Component for NavToContributing
 */
export default class NavToContributing extends Component {
  /**
   * react render override
   * @return {JSX.Element}
   */
  render() {
    return (
      <div className="nav">
        <Link to="/contributing">Go to contributing page</Link>
      </div>
    );
  }
}
