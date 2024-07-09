from pyclashbot.bot.event_dispatcher import event_dispatcher


def increment_bot_failures():
    event_dispatcher.increment_stat.emit("Bot Failures")


def increment_wins():
    event_dispatcher.increment_stat.emit("Wins")


def increment_losses():
    event_dispatcher.increment_stat.emit("Losses")


def stat_tester():
    increment_bot_failures()
    increment_wins()
    increment_losses()
    print("test")
