import React, { Component } from 'react';
import { testBadgeEvent } from '../../GoogleAnalytics';

/**
* Component for latest release download link
*/
export default class TestBadge extends Component
{

    render()
    {
        return (
            <a href="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml" rel="nofollow" onClick={() => testBadgeEvent()}>
                <img
                    src="https://github.com/matthewmiglio/py-clash-bot/actions/workflows/python-tests.yml/badge.svg"
                    alt="GitHub Python tests badge" />
            </a>
        );
    }
}