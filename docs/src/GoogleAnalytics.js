import ReactGA from "react-ga4";
import { process } from "process";

const GA_MEASUREMENT_ID = "G-Y7520HNKMG";

/**
 * Initialize google analytics with tracking ID and settings
 */
export function initializeGA() {
  const isDev = process.env.NODE_ENV === "development";
  ReactGA.initialize(GA_MEASUREMENT_ID, {
    gaOptions: {
      debug_mode: isDev,
      cookieDomain: "matthewmiglio.github.io",
      cookieFlags: "SameSite=None; Secure",
    },
    gtagOptions: { debug_mode: isDev },
    debug: isDev,
  });
}

/**
 * updates reactga with a page change
 * @param {string} page The page to update ReactGA with.
 */
export function pageChange(page) {
  ReactGA.send({
    hitType: "pageview",
    page: window.location.pathname + window.location.search,
  });
}

// Track link clicks
export const handleClick = (event) => {
  ReactGA.event({
    category: "Outbound Link",
    action: "Click",
    label: event.currentTarget.href,
  });
};

export const handleDownload = (event, downloadLink) => {
  ReactGA.event({
    category: "Release",
    action: "Download",
    label: downloadLink,
  });
};
