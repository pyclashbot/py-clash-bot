

from itertools import cycle
import subprocess
import sys
import time

from pyclashbot.__main__ import initialize_client, main_loop, restart_state
from pyclashbot.configuration import load_user_settings
from pyclashbot.logger import Logger

user_settings = load_user_settings()
ssids = cycle(user_settings['selected_accounts'])
launcher_path=user_settings['MEmu_Multi_launcher_path']
logger = Logger()
ssid = next(ssids)
loop_count = 0

print(launcher_path)



jobs = ['Fight', 'Request', 'Donate', 'Upgrade_cards', 'Collect_battlepass_rewards', 'Collect_mastery_rewards']
main_loop(jobs)