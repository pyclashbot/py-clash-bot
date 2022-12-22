import React from "react";

import "./App.css";

import Controls from "./components/Controls";
import Stats from "./components/Stats";
import AppHeader from "./components/AppHeader";
import Output from "./components/Output";

import {
  startThread,
  stopThread,
  pauseThreadToggle,
  readFromServer,
} from "./functions/threadCommunication";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      statistics: {},
      pollTimer: null,

      //backend thread states
      threadStarted: false,
      threadPaused: false,
    };
  }

  startThread = async (selectedJobs, selectedAccounts) => {
    // parse out only the value of the selected jobs
    const data = await startThread(selectedJobs, selectedAccounts);

    this.setState({ threadStarted: data.status === "started" });
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

  readFromServer = async () => {
    const data = await readFromServer();

    if (data.status === "stopped" || data.status === "errored") {
      // Stop timer if thread is stopped
      clearInterval(this.state.pollTimer);
      this.setState({ pollTimer: null });
      this.setState({ threadStarted: false });
    }
    this.setState({ statistics: data.statistics ?? {} });
    this.setState({ output: data.message ?? "Waiting for response..." });
  };

  stopThread = async () => {
    await stopThread();
    this.setState({ threadStarted: false });
    clearInterval(this.state.pollTimer);
    this.setState({ pollTimer: null });
  };

  pauseThreadToggle = async () => {
    const data = await pauseThreadToggle();
    // if data.status is "stopped", then thread is stopped and not paused
    // if data.status is "paused", then thread is paused
    // if data.status is "resumed", then thread is not paused
    this.setState({
      threadPaused: data.status === "paused" && data.status !== "resumed",
    });

    if (data.status === "stopped") {
      clearInterval(this.state.pollTimer);
      this.setState({ pollTimer: null });
      this.setState({ threadStarted: false });
      this.setState({ threadPaused: false });
    }
  };

  render() {
    return (
      <div className="AppContainer">
        <AppHeader />
        <div
          style={{
            marginTop: 0,
            marginBottom: 8,
            paddingTop: 5,
            paddingBottom: 5,
            paddingLeft: 10,
            paddingRight: 10,
            backgroundColor: "#C0C0C0",
            boxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
            WebkitBoxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
            MozBoxShadow: "-2px -2px 0px #FFFFFF, 2px 2px 0px #000000",
          }}
        >
          <Controls
            startThread={this.startThread}
            stopThread={this.stopThread}
            pauseThreadToggle={this.pauseThreadToggle}
            threadStarted={this.state.threadStarted}
            threadPaused={this.state.threadPaused}
          />
          <Stats statistics={this.state.statistics} />
          <Output
            threadStarted={this.state.threadStarted}
            output={this.state.output}
          />
        </div>
      </div>
    );
  }
}

export default App;
