import { Component } from 'react';


const api_url = 'https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest';


/**
* Component for time since last release
*/
export default class ReleaseUpdate extends Component
{
    constructor(props)
    {
        super(props);
        this.state = {
            last_updated: []
        };
    }

    GetLatestReleaseInfo()
    {
        fetch(api_url)
            .then(response => response.json())
            .then(data =>
            {
                const oneHour = 60 * 60 * 1000;
                const oneDay = 24 * oneHour;
                var dateDiff = new Date() - new Date(data.assets[0].updated_at);
                // eslint-disable-next-line eqeqeq
                var timeAgo = dateDiff < oneDay ? `${(dateDiff / oneHour).toFixed()} ${(dateDiff / oneHour).toFixed() == 1 ? 'hour' : 'hours'} ago` : `${(dateDiff / oneDay).toFixed()} days ago`;
                this.setState({ last_updated: timeAgo });
            });
    }
    componentDidMount()
    {
        this.GetLatestReleaseInfo();
    }
    render()
    {
        return (
            this.state.last_updated
        );
    }
}