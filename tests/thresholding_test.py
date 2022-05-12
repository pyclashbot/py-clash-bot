from PIL import Image
from pyclashbot.__main__ import compare_images

# between test_image and pass_template, detection above 0.66
# between test_iamge and fail_template, no detection
# between clashss and clashtemp, detection about 0.96

ss = Image.open("tests/assets/clashss.png")
tp = Image.open("tests/assets/clashtemp.png")

granularity = 100

for i in range(granularity):
    print(f"{i/granularity} : {compare_images(ss, tp, i/granularity)}")
