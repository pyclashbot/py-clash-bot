// nextjs api route for notification data
// https://nextjs.org/docs/api-routes/introduction

// this route should handle reading notifications from notifications.json.
// on build the notifications.json file should be read and the contents

import { readFileSync } from "fs";
import path from "path";

const notificationsPath = path.join(process.cwd(), "notifications.json");

export function getNotifications() {
  const fileContents = readFileSync(notificationsPath, "utf8");
  return JSON.parse(fileContents);
}

// since this is a static site, we can't use the api route to read the notifications.json file
// we could try using getStaticProps to read the file and pass it to the component, but
// will this work with nextjs's API routes?

export async function getStaticProps() {
  const notifications = getNotifications();
  return {
    props: {
      notifications,
    },
  };
}

export default function handler(req, res) {
  // return the notifications from props?
  const notifications = //???
  res.status(200).json(notifications);
}
