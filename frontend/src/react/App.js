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
      statistics: {
        wins: 0,
        losses: 0,
        fights: 0,
        requests: 0,
        auto_restarts: 0,
        restarts_after_failure: 0,
        chests_unlocked: 0,
        cards_played: 0,
        cards_upgraded: 0,
        account_switches: 0,
        card_mastery_reward_collections: 0,
        battlepass_rewards_collections: 0,
        level_up_chest_collections: 0,
        war_battles_fought: 0,
        free_offer_collections: 0,
        daily_challenge_reward_collections: 0,
        war_chest_collections: 0,
        current_status: 0,
        time_since_start: "0:00:00",
      },
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
                  { title: "Wins:", value: this.state.statistics.wins },
                  { title: "Losses:", value: this.state.statistics.losses },
                  {
                    title: "Cards Played:",
                    value: this.state.statistics.cards_played,
                  },
                  { title: "2v2 Fights:", value: this.state.statistics.fights },
                  {
                    title: "War Fights:",
                    value: this.state.statistics.war_battles_fought,
                  },
                ]}
                columnCount="1"
              />
            </BoxFrame>
            <BoxFrame title="Progress">
              <StatsGrid
                stats={[
                  { title: "Requests:", value: this.state.statistics.requests },
                  {
                    title: "Chests Opened:",
                    value: this.state.statistics.chests_unlocked,
                  },
                  {
                    title: "Cards Upgraded:",
                    value: this.state.statistics.cards_upgraded,
                  },
                  {
                    title: "Acount Switches:",
                    value: this.state.statistics.account_switches,
                  },
                  {
                    title: "Automatic Restarts:",
                    value: this.state.statistics.auto_restarts,
                  },
                  {
                    title: "Restarts:",
                    value: this.state.statistics.restarts_after_failure,
                  },
                ]}
                columnCount="1"
              />
            </BoxFrame>
            <BoxFrame title="Collection">
              <StatsGrid
                stats={[
                  {
                    title: "Card Master Reward:",
                    value:
                      this.state.statistics.card_mastery_reward_collections,
                  },
                  {
                    title: "Battlepass Reward:",
                    value: this.state.statistics.battlepass_rewards_collections,
                  },
                  {
                    title: "Lvl Up Chest:",
                    value: this.state.statistics.level_up_chest_collections,
                  },
                  {
                    title: "Free Offer:",
                    value: this.state.statistics.free_offer_collections,
                  },
                  {
                    title: "War Chest:",
                    value: this.state.statistics.war_chest_collections,
                  },
                  {
                    title: "Daily Challenge:",
                    value:
                      this.state.statistics.daily_challenge_reward_collections,
                  },
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
