import axios from "axios";

const BACKEND_BASE_URL = "http://localhost:1357";

const handleError = (err) => {
  // Handle error
  if (err.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.log(err.response.data);
    console.log(err.response.status);
    console.log(err.response.headers);
  } else if (err.request) {
    // The request was made but no response was received
    // `err.request` is an instance of XMLHttpRequest in the browser and an instance of
    // http.ClientRequest in node.js
    console.log(err.request);
  } else {
    // Something happened in setting up the request that triggered an Error
    console.log("Error", err.message);
  }
};

export const startThread = async (selectedJobs, selectedAccounts) => {
  try {
    // Make POST request to start thread
    const res = await axios.post(
      BACKEND_BASE_URL + "/start-thread",
      {
        selectedJobs: selectedJobs,
        selectedAccounts: selectedAccounts,
      },
      { withCredentials: true }
    );

    return res.data ?? {};
  } catch (err) {
    handleError(err);
  }
};

export const stopThread = async () => {
  try {
    // Make GET request to stop thread
    await axios.get(BACKEND_BASE_URL + "/stop-thread");
  } catch (err) {
    handleError(err);
  }
};

export const pauseThreadToggle = async () => {
  try {
    // Make GET request to pause thread
    const res = await axios.get(BACKEND_BASE_URL + "/toggle-pause-thread");

    return res.data ?? {};
  } catch (err) {
    handleError(err);
  }
};

export const readFromServer = async () => {
  try {
    // Make GET request to read from server
    const res = await axios.get(BACKEND_BASE_URL + "/output");

    return res.data ?? {};
  } catch (err) {
    handleError(err);
  }
};
