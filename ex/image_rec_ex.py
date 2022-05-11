from PIL import Image
from pyautogui import screenshot
from test7 import image_rec


# Use pyautogui to screnshot
ss = screenshot()

# show screenshot
ss.show()

# load template image from file
tp = Image.open("play.png")

# show loaded template
tp.show()

# run image rec and print output
print(image_rec(ss, tp))
