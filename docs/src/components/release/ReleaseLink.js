import React, { Component } from 'react';
import { releaseLinkEvent } from '../../GoogleAnalytics';



const api_url = 'https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest';


/**
* Component for latest release download link
*/
export default class ReleaseLink extends Component
{
    constructor(props)
    {
        super(props);
        this.state = {
            release_url: []
        };
    }

    GetLatestReleaseInfo()
    {
        fetch(api_url)
            .then(response => response.json())
            .then(data =>
            {
                this.setState({ release_url: data.assets[0].browser_download_url });
                var downloadCount = 0;
                for (let asset in data.assets)
                {
                    downloadCount = downloadCount + asset.download_count;
                }
                this.setState({ download_count: downloadCount });
                this.setState({ last_updated: data.assets[0].updated_at });
            });
    }
    componentDidMount()
    {
        this.GetLatestReleaseInfo();
    }
    render()
    {
        return (
            <p><a className='download' href={this.state.release_url} onClick={() => releaseLinkEvent()}>
                Download the latest release
            </a></p>
        );
    }
}