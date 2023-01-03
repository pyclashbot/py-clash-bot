import React from "react";

import BoxFrame from "./BoxFrame";
import StatsGrid from "./StatsGrid";

function Stats({statistics}) {
  return (
    <div className="stats-block" style={{ display: "flex", marginTop: "10px" }}>
      <BoxFrame title="Battle" style={{ flexGrow: "1" }}>
        <StatsGrid
          stats={[
            { title: "Wins:", value: statistics.wins ?? 0 },
            {
              title: "Losses:",
              value: statistics.losses ?? 0,
            },
            {
              title: "Cards Played:",
              value: statistics.cards_played ?? 0,
            },
            {
              title: "2v2 Fights:",
              value: statistics.fights ?? 0,
            },
            {
              title: "War Fights:",
              value: statistics.war_battles_fought ?? 0,
            },
          ]}
          columnCount="1"
        />
      </BoxFrame>
      <BoxFrame title="Progress" style={{ flexGrow: "1" }}>
        <StatsGrid
          stats={[
            {
              title: "Requests:",
              value: statistics.requests ?? 0,
            },
            {
              title: "Chests Opened:",
              value: statistics.chests_unlocked ?? 0,
            },
            {
              title: "Cards Upgraded:",
              value: statistics.cards_upgraded ?? 0,
            },
            {
              title: "Acount Switches:",
              value: statistics.account_switches ?? 0,
            },
            {
              title: "Automatic Restarts:",
              value: statistics.auto_restarts ?? 0,
            },
            {
              title: "Restarts:",
              value: statistics.restarts_after_failure ?? 0,
            },
          ]}
          columnCount="1"
        />
      </BoxFrame>
      <BoxFrame title="Collection" style={{ flexGrow: "1" }}>
        <StatsGrid
          stats={[
            {
              title: "Card Master Reward:",
              value: statistics.card_mastery_reward_collections ?? 0,
            },
            {
              title: "Battlepass Reward:",
              value: statistics.battlepass_rewards_collections ?? 0,
            },
            {
              title: "Lvl Up Chest:",
              value: statistics.level_up_chest_collections ?? 0,
            },
            {
              title: "Free Offer:",
              value: statistics.free_offer_collections ?? 0,
            },
            {
              title: "War Chest:",
              value: statistics.war_chest_collections ?? 0,
            },
            {
              title: "Daily Challenge:",
              value: statistics.daily_challenge_reward_collections ?? 0,
            },
          ]}
          columnCount="1"
        />
      </BoxFrame>
    </div>
  );
}

export default Stats;
