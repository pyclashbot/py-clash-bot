import React from "react";

import "./App.css";
import JobDropDown from "./components/JobDropDown";
import AccountDropDown from "./components/AccountDropDown";
import BoxFrame from "./components/BoxFrame";
import StatsGrid from "./components/StatsGrid";
import AppHeader from "./components/AppHeader";
import ThreadTimer from "./components/ThreadTimer";

import {
  startThread,
  stopThread,
  readFromServer,
} from "./functions/threadCommunication";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedJobs: [],
      selectedAccounts: null,
      statistics: {},
      pollTimer: null,

      //backend thread states
      threadStarted: false,
      threadPaused: false,
    };
  }

  startThread = async () => {
    // parse out only the value of the selected jobs
    const selectedJobs = this.state.selectedJobs.map((job) => job.value);
    const selectedAccounts = this.state.selectedAccounts.value;
    const data = await startThread(selectedJobs, selectedAccounts);

    this.setState({ threadStarted: data.status === "started"});
    this.setState({ output: data.message ?? "" });

    const timer = setInterval(() => {
      this.readFromServer().catch(() => {
        // Stop timer if reading from server fails
        clearInterval(timer);
        this.setState({ threadStarted: false });
      });
    }, 1000); // Read from server every second

    // Save timer to state
    this.setState({ pollTimer: timer });
  };

  stopThread = async () => {
    await stopThread();
    this.setState({ threadStarted: false });
    clearInterval(this.state.pollTimer);
    this.setState({ pollTimer: null });
  };

  readFromServer = async () => {
    const data = await readFromServer();

    this.setState({ statistics: data.statistics ?? {} });
    this.setState({ output: data.message ?? "Waiting for response..." });
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
                  { title: "Wins:", value: this.state.statistics.wins ?? 0 },
                  {
                    title: "Losses:",
                    value: this.state.statistics.losses ?? 0,
                  },
                  {
                    title: "Cards Played:",
                    value: this.state.statistics.cards_played ?? 0,
                  },
                  {
                    title: "2v2 Fights:",
                    value: this.state.statistics.fights ?? 0,
                  },
                  {
                    title: "War Fights:",
                    value: this.state.statistics.war_battles_fought ?? 0,
                  },
                ]}
                columnCount="1"
              />
            </BoxFrame>
            <BoxFrame title="Progress">
              <StatsGrid
                stats={[
                  {
                    title: "Requests:",
                    value: this.state.statistics.requests ?? 0,
                  },
                  {
                    title: "Chests Opened:",
                    value: this.state.statistics.chests_unlocked ?? 0,
                  },
                  {
                    title: "Cards Upgraded:",
                    value: this.state.statistics.cards_upgraded ?? 0,
                  },
                  {
                    title: "Acount Switches:",
                    value: this.state.statistics.account_switches ?? 0,
                  },
                  {
                    title: "Automatic Restarts:",
                    value: this.state.statistics.auto_restarts ?? 0,
                  },
                  {
                    title: "Restarts:",
                    value: this.state.statistics.restarts_after_failure ?? 0,
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
                      this.state.statistics.card_mastery_reward_collections ??
                      0,
                  },
                  {
                    title: "Battlepass Reward:",
                    value:
                      this.state.statistics.battlepass_rewards_collections ?? 0,
                  },
                  {
                    title: "Lvl Up Chest:",
                    value:
                      this.state.statistics.level_up_chest_collections ?? 0,
                  },
                  {
                    title: "Free Offer:",
                    value: this.state.statistics.free_offer_collections ?? 0,
                  },
                  {
                    title: "War Chest:",
                    value: this.state.statistics.war_chest_collections ?? 0,
                  },
                  {
                    title: "Daily Challenge:",
                    value:
                      this.state.statistics
                        .daily_challenge_reward_collections ?? 0,
                  },
                ]}
                columnCount="1"
              />
            </BoxFrame>
          </div>
          <div className="output-block">
            <ThreadTimer isActive={this.state.threadStarted} />
            <input
              className="status"
              value={this.state.output ?? "Idle"}
              readOnly
            />
          </div>
        </div>
      </div>
    );
  }
}

export default App;
