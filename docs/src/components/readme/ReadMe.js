import Dependencies from './Dependencies';
import Description from './Description';
import Execution from './Execution';
import Install from './Install';
import React, {Component} from 'react';
import NavToContributing from '../navigation/ToContributing';

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
      <div className="mume markdown-preview  ">
        <Description/>
        <Install/>
        <Dependencies/>
        <Execution/>
        <NavToContributing/>
      </div>
    );
  }
}
