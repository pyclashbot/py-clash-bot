import dynamic from "next/dynamic";

import { initializeGA } from "../GoogleAnalytics";

const SEO = dynamic(() => import("../components/SEO"));
const ReadMe = dynamic(() => import("../components/readme/ReadMe"));

initializeGA();

export default function Home() {
  return (
    <>
      <SEO
        title="py-clash-bot"
        description="A Clash Royale automation bot written in Python"
      />
      <ReadMe />
    </>
  );
}
