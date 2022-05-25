import { Component } from 'react';


const api_url = 'https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest';


/**
* Component for release download count
*/
export default class ReleaseDownloadCount extends Component
{
    constructor(props)
    {
        super(props);
        this.state = {
            download_count: []
        };
    }

    GetLatestReleaseInfo()
    {
        fetch(api_url)
            .then(response => response.json())
            .then(data =>
            {
                var downloadCount = 0;
                for (var i = 0; i < data.assets.length; i++)
                {
                    downloadCount += data.assets[i].download_count;
                }
                this.setState({ download_count: downloadCount });
            });
    }
    componentDidMount()
    {
        this.GetLatestReleaseInfo();
    }
    render()
    {
        return (
            this.state.download_count
        );
    }
}