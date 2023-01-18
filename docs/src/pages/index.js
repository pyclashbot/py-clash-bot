import dynamic from "next/dynamic";

import { initializeGA } from "../GoogleAnalytics";

const Header = dynamic(() => import("../components/Header"));
const ReadMe = dynamic(() => import("../components/readme/ReadMe"));

initializeGA();

export default function Home() {
  return (
    <>
      <Header
        title="py-clash-bot"
        description="A Clash Royale automation bot written in Python"
      />
      <ReadMe />
    </>
  );
}
