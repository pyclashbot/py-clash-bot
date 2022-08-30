import React, {Component} from 'react';
import ContributionDescription from './ContributionDescription';
import DevInstall from './DevInstall';
import BugReport from './BugReport';
import NavToReadme from '../navigation/NavToReadme';


/**
* Component for project description
*/
export default class Contributing extends Component {
  /**
     * react render override
     * @return {JSX.Element}
     */
  render() {
    return (
      <div className="mume markdown-preview  ">
        <ContributionDescription/>
        <BugReport/>
        <DevInstall/>
        <NavToReadme/>
      </div>
    );
  }
}
