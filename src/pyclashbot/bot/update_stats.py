from pyclashbot.bot.event_dispatcher import event_dispatcher


def increment_bot_failures():
    event_dispatcher.increment_stat.emit("Bot Failures")


def increment_wins():
    event_dispatcher.increment_stat.emit("Wins")


def increment_losses():
    event_dispatcher.increment_stat.emit("Losses")


def increment_legends_fights():
    event_dispatcher.increment_stat.emit("Path of legends fights")


def increment_trophy_fights():
    event_dispatcher.increment_stat.emit("Trophy fights")


def incremenet_queens_fights():
    event_dispatcher.increment_stat.emit("Queens 1v1 fights")


def increment_2v2_fights():
    event_dispatcher.increment_stat.emit("2v2 fights")


def increment_war_fights():
    event_dispatcher.increment_stat.emit("War fights")


def increment_random_decks():
    event_dispatcher.increment_stat.emit("Deck randomization")


def increment_cards_played():
    event_dispatcher.increment_stat.emit("Cards played")


def increment_requests():
    event_dispatcher.increment_stat.emit("Requests")


def increment_shop_buys():
    event_dispatcher.increment_stat.emit("Shop purchases")


def increment_donates():
    event_dispatcher.increment_stat.emit("Donates")


def increment_chest_unlocks():
    event_dispatcher.increment_stat.emit("Chests unlocked")


def increment_daily_rewards():
    event_dispatcher.increment_stat.emit("Daily rewards")


def increment_mastery_collects():
    event_dispatcher.increment_stat.emit("Card mastery collects")


def increment_bannerbox_collects():
    event_dispatcher.increment_stat.emit("Bannerbox collects")


def increment_cards_upgraded():
    event_dispatcher.increment_stat.emit("Cards upgraded")


def increment_battlepass_collects():
    event_dispatcher.increment_stat.emit("Battlepass collects")


def increment_level_up_chests():
    event_dispatcher.increment_stat.emit("Level up collects")


def increment_war_chests():
    event_dispatcher.increment_stat.emit("War chest collects")


def increment_season_shop_buys():
    event_dispatcher.increment_stat.emit("Season shop purchases")


def stat_tester():
    increment_bot_failures()
    increment_wins()
    increment_losses()
    increment_legends_fights()
    increment_trophy_fights()
    incremenet_queens_fights()
    increment_2v2_fights()
    increment_war_fights()
    increment_random_decks()
    increment_requests()
    increment_shop_buys()
    increment_donates()
    increment_chest_unlocks()
    increment_daily_rewards()
    increment_mastery_collects()
    increment_bannerbox_collects()
    increment_cards_upgraded()
    increment_battlepass_collects()
    increment_level_up_chests()
    increment_war_chests()
    increment_season_shop_buys()
    print("test")
