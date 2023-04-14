// nextjs api route for notification data
// https://nextjs.org/docs/api-routes/introduction
import type { NextApiRequest, NextApiResponse } from "next";
import process from "process";
import notifications from "../../assets/notifications.json";
import { GA_MEASUREMENT_ID } from "../../GoogleAnalytics";

const is_dev = process.env.NODE_ENV !== "production";

function sendAnalytics(req: NextApiRequest) {
  const API_SECRET = process.env.MP_API_KEY;
  if (!API_SECRET) {
    console.error("MP_API_KEY not set");
    return;
  }

  const API_URL = is_dev
    ? "https://www.google-analytics.com/debug/mp/collect"
    : "https://www.google-analytics.com/mp/collect";

  const url = new URL(API_URL);
  url.searchParams.append("measurement_id", GA_MEASUREMENT_ID);
  url.searchParams.append("api_secret", API_SECRET);

  const event = {
    client_id: req.cookies._ga ?? "unknown",
    events: [
      {
        name: "notification",
        params: {
          url: req.headers.referer,
          query: JSON.stringify(req.query),
          user_agent: req.headers["user-agent"],
          accept_language: req.headers["accept-language"],
        },
      },
    ],
  };

  const mp_res = fetch(url.toString(), {
    method: "POST",
    body: JSON.stringify(event),
  });

  if (is_dev) {
    console.log(JSON.stringify(event));
    mp_res.then((res) => res.json()).then((data) => console.log(data));
  }
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  sendAnalytics(req);

  // latest query param returns only the latest notification
  if (req.query.latest) {
    res.status(200).json(notifications[0]);
  } else {
    res.status(200).json(notifications);
  }
}
