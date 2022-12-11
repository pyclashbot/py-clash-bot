import ReactGA from 'react-ga4';

/**
 * Initialize google analytics with tracking ID and settings
 */
export function initializeGA() {
  ReactGA.initialize('G-Y7520HNKMG');
}

/**
 * updates reactga with a page change
 * @param {string} page The page to update ReactGA with.
 */
export function pageChange(page) {
  ReactGA.send({
    hitType: 'pageview',
    page: window.location.pathname + window.location.search,
  });
  const devQuery = '?utm_source=dev&utm_medium=dev';
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
