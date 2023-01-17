import SEO from "../components/SEO";
import ReadMe from "../components/readme/ReadMe";
import { initializeGA } from "../GoogleAnalytics";

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
