import time
import random
from pyclashbot.bot.stats import stats



#simulate running a fight in the backend and updateing the gui with values
def do_fight():
    fight_duration = 10#s
    start_time = time.time()

    print(f'Simulating a fight for {fight_duration} seconds')

    while time.time() - start_time < fight_duration:
        #randomly update values
        if random.randint(1,3)== 1:
            stats.increment_wins()
            print('incrementing wins')
        if random.randint(1,3)== 1:
            stats.increment_losses()
            print('incrementing losses')

        time.sleep(0.3)

    return True

