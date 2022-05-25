import React, { Component } from 'react';
import SourceBadgeSVG from '../../assets/source_badge.svg';
import { sourceBadgeEvent } from '../../GoogleAnalytics';

/**
* Component for latest release download link
*/
export default class SourceBadge extends Component
{

    render()
    {
        return (
            <a
                href="https://github.com/matthewmiglio/py-clash-bot/"
                rel="nofollow"
                onClick={() => sourceBadgeEvent()}>
                <img
                    src={SourceBadgeSVG}
                    alt="Link to Source on GitHub" />
            </a>
        );
    }
}