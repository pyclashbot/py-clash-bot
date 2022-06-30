


from pyclashbot.board_scanner import get_board_screenshot, get_red_pix_from_ss, show_red_pix
from pyclashbot.logger import Logger

logger= Logger()


while True:
    red_pix_list = get_red_pix_from_ss(get_board_screenshot())
    show_red_pix(red_pix_list)
