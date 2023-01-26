import { Component } from "react";

const apiUrl =
  "https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest";

/**
 * Component for time since last release
 */
export default class ReleaseUpdate extends Component {
  /**
   * constructor to set states
   * @param {*} props component props
   */
  constructor(props) {
    super(props);
    this.state = {
      last_updated: [],
    };
  }

  /**
   * make api call to get time since release
   */
  getLatestReleaseInfo() {
    fetch(apiUrl)
      .then((response) => response.json())
      .then((data) => {
        const oneHour = 60 * 60 * 1000;
        const oneDay = 24 * oneHour;
        const dateDiff = new Date() - new Date(data.assets[0].updated_at);
        // eslint-disable-next-line eqeqeq
        let daysAgo = Number((dateDiff / oneDay).toFixed());
        daysAgo = `${daysAgo} ${daysAgo === 1 ? "day" : "days"} ago`;
        let hoursAgo = Number((dateDiff / oneHour).toFixed());
        hoursAgo = `${hoursAgo} ${hoursAgo === 1 ? "hour" : "hours"} ago`;
        const timeAgo = dateDiff < oneDay ? hoursAgo : daysAgo;
        this.setState({ last_updated: timeAgo });
      });
  }
  /**
   * on mount get release info
   */
  componentDidMount() {
    this.getLatestReleaseInfo();
  }
  /**
   * react render override
   * @return {string}
   */
  render() {
    return `Release last updated ${this.state.last_updated} `;
  }
}
