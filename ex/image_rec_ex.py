from PIL import Image
from pyautogui import screenshot
from test7 import compare_images


# Use pyautogui to screnshot
ss = screenshot()

# show screenshot
ss.show()

# load template image from file
tp = Image.open("play.png")

# show loaded template
tp.show()

# run image rec and print output
print(compare_images(ss, tp))
