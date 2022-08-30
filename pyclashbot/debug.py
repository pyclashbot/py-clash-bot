

from itertools import cycle
import subprocess
import sys
import time

from pyclashbot.__main__ import initialize_client, restart_state
from pyclashbot.configuration import load_user_settings
from pyclashbot.logger import Logger

user_settings = load_user_settings()
ssids = cycle(user_settings['selected_accounts'])
launcher_path=user_settings['MEmu_Multi_launcher_path']
logger = Logger()
ssid = next(ssids)
loop_count = 0

print(launcher_path)


# def open_memu_launcher(launcher_path):
#     logger.log("Opening launcher.")
#     try:
#         subprocess.Popen(launcher_path)
#     except FileNotFoundError:
#         print(r"Launcher path not found, edit config file: %appdata%\py-TarkBot\config.json")
#         sys.exit("Launcher path not found")
#     time.sleep(10)



create