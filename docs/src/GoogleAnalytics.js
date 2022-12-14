import ReactGA from 'react-ga4';

const GA_MEASUREMENT_ID = 'G-Y7520HNKMG';

/**
 * Initialize google analytics with tracking ID and settings
 */
export function initializeGA() {
  ReactGA.initialize(GA_MEASUREMENT_ID);
}

/**
 * updates reactga with a page change
 * @param {string} page The page to update ReactGA with.
 */
export function pageChange(page) {
  const devQuery = '?utm_source=dev&utm_medium=dev';
  if (window.location.href.split('/').pop() == devQuery) {
    ReactGA.initialize(GA_MEASUREMENT_ID, {
      gaOptions: {
        debug_mode: true,
      },
      gtagOptions: {
        debug_mode: true,
      },
    });
  }
  ReactGA.send({
    hitType: 'pageview',
    page: window.location.pathname + window.location.search,
  });

  if (
    window.location.href.split('/').pop() !== devQuery &&
    // eslint-disable-next-line no-undef
    (!process.env.NODE_ENV || process.env.NODE_ENV === 'development')
  ) {
    window.location.href = page + devQuery;
  }
}

// Track link clicks
export const handleClick = (event) => {
  ReactGA.event({
    category: 'Outbound Link',
    action: 'Click',
    label: event.currentTarget.href,
  });
};

export const handleDownload = (event) => {
  ReactGA.event({
    category: 'Release',
    action: 'Download',
    label: event.currentTarget.href,
  });
};
