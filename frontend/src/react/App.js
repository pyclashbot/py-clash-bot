import React from "react";
import axios from "axios";

import "./App.css";
import JobDropDown from "./components/JobDropDown";
import AccountDropDown from "./components/AccountDropDown";
import BoxFrame from "./components/BoxFrame";
import StatsGrid from "./components/StatsGrid";
import AppHeader from "./components/AppHeader";

const FLASK_BASE_URL = "http://localhost:1357";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedJobs: [],
      selectedAccounts: null,
      statistics: [
        { title: "test0:", value: "test0" },
        { title: "test1:", value: "test1" },
        { title: "test2:", value: "test2" },
        { title: "test3:", value: "test3" },
        { title: "test4:", value: "test4" },
        { title: "test5:", value: "test5" },
      ],
      output: "",
      thread: null,

      //backend thread states
      threadStarted: false,
      threadPaused: false,
    };
  }

  startThread = async () => {
    try {
      // parse out only the value of the selected jobs
      const selectedJobs = this.state.selectedJobs.map((job) => job.value);
      const selectedAccounts = this.state.selectedAccounts.value;

      // Make POST request to start thread
      const res = await axios.post(
        FLASK_BASE_URL + "/start-thread",
        {
          selectedJobs: selectedJobs,
          selectedAccounts: selectedAccounts,
        },
        { withCredentials: true }
      );

      this.setState({ threadStarted: true });

      // Update output with response message
      this.setState({ output: res.data.message });

      // Start timer to periodically read from server
      this.startReadFromServerTimer();
    } catch (err) {
      // Handle error
    }
  };

  startReadFromServerTimer = () => {
    const timer = setInterval(() => {
      this.readFromServer().catch(() => {
        // Stop timer if reading from server fails
        clearInterval(timer);
      });
    }, 3000); // Read from server every 3 seconds

    // Save timer to state
    this.setState({ thread: timer });
  };

  stopThread = async () => {
    try {
      // Make GET request to stop thread
      await axios.get(FLASK_BASE_URL + "/stop-thread");

      this.setState({ threadStarted: false });
      // Clear timer
      clearInterval(this.state.thread);
      this.setState({ thread: null });
    } catch (err) {
      // Handle error
    }
  };

  readFromServer = async () => {
    try {
      // Make GET request to read from server
      const res = await axios.get(FLASK_BASE_URL + "/output");

      // Update output with response data
      this.setState({ statistics: res.data.statistics });
      this.setState({ output: res.data.message });
    } catch (err) {
      // Handle error
    }
  };

  updateSelectedJobs = (selectedJobs) => {
    this.setState({ selectedJobs });
  };

  updateSelectedAccounts = (selectedAccounts) => {
    this.setState({ selectedAccounts });
  };

  render() {
    return (
      <div className="AppContainer">
        <AppHeader />
        <div className="block">
          <div className="button-block">
            <div className="account-block">
              <AccountDropDown
                selectedOptions={this.state.selectedAccounts}
                onChange={this.updateSelectedAccounts}
              />
            </div>
            <button
              onClick={this.startThread}
              disabled={this.state.threadStarted}
            >
              Start
            </button>
            <button disabled={!this.state.threadStarted}>
              {!this.state.threadPaused ? "Pause" : "resume"}
            </button>
            <button
              onClick={this.stopThread}
              disabled={!this.state.threadStarted}
            >
              Stop
            </button>
          </div>
          <div className="job-block">
            <JobDropDown
              selectedOptions={this.state.selectedJobs}
              onChange={this.updateSelectedJobs}
            />
          </div>
          <div className="stats-block">
            <BoxFrame title="Battle">
              <StatsGrid
                stats={[
                  { title: "Wins:", value: "0" },
                  { title: "Losses:", value: "1" },
                  { title: "Cards Played:", value: "2" },
                  { title: "2v2 Fights:", value: "3" },
                  { title: "War Fights:", value: "4" },
                ]}
                columnCount="1"
              />
            </BoxFrame>
            <BoxFrame title="Progress">
              <StatsGrid
                stats={[
                  { title: "Requests:", value: "0" },
                  { title: "Chests Opened:", value: "1" },
                  { title: "Cards Upgraded:", value: "2" },
                  { title: "Acount Switches:", value: "3" },
                  { title: "Automatic Restarts:", value: "4" },
                  { title: "Restarts:", value: "5" },
                ]}
                columnCount="1"
              />
            </BoxFrame>
            <BoxFrame title="Collection">
              <StatsGrid
                stats={[
                  { title: "Card Master Reward:", value: "1" },
                  { title: "Battlepass Reward:", value: "2" },
                  { title: "Lvl Up Chest:", value: "3" },
                  { title: "Free Offer:", value: "4" },
                  { title: "War Chest:", value: "5" },
                  { title: "Daily Challenge:", value: "6" },
                ]}
                columnCount="1"
              />
            </BoxFrame>
          </div>
          <input
            className="status"
            placeholder="Idle"
            value={this.state.output}
            readOnly
          />
        </div>
      </div>
    );
  }
}

export default App;
