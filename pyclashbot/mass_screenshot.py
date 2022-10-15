
import time
from os.path import join

import numpy
import pyautogui
from PIL import Image

from pyclashbot.client import screenshot


def screenshot_around_mouse():
    # takes pics to the bottom left of the mouse
    origin = pyautogui.position()

    r1 = [origin[0], origin[1], 33, 10]
    ss_1 = pyautogui.screenshot(region=(r1))  # type: ignore
    ss_1.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_1.png')

    r2 = [origin[0], origin[1], 38, 10]
    ss_2 = pyautogui.screenshot(region=(r2))  # type: ignore
    ss_2.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_2.png')

    r3 = [origin[0], origin[1], 45, 15]
    ss_3 = pyautogui.screenshot(region=(r3))  # type: ignore
    ss_3.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_3.png')

    r4 = [origin[0], origin[1], 20, 15]
    ss_4 = pyautogui.screenshot(region=(r4)) # type: ignore
    ss_4.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_4.png')

    r5 = [origin[0], origin[1], 25, 20]
    ss_5 = pyautogui.screenshot(region=(r5)) # type: ignore
    ss_5.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_5.png')

    r6 = [origin[0], origin[1], 30, 20]
    ss_6 = pyautogui.screenshot(region=(r6)) # type: ignore
    ss_6.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_6.png')

    r7 = [origin[0], origin[1], 35, 25]
    ss_7 = pyautogui.screenshot(region=(r7)) # type: ignore
    ss_7.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_7.png')

    r8 = [origin[0], origin[1], 40, 25]
    ss_8 = pyautogui.screenshot(region=(r8)) # type: ignore
    ss_8.save(r'C:\Users\Matt\Desktop\inc_pics\ifhy_8.png')


def take_many_screenshots(
        duration,
        frequency,
        region=None,
        name=None,
        folder=None):
    """_summary_

    Args:
        duration (float): seconds to take screenshots
        frequency (float): screenshot per second
        region (tuple[int], optional): screenshot region. Defaults to None.
        name (str, optional): screenshot save name. Defaults to None.
        folder (str, optional): screenshot save folder. Defaults to None.
    """
    number_of_screenshots = duration * frequency
    interval = 1 / frequency
    screenshots = []

    # take screenshots
    for _ in range(number_of_screenshots):
        ss = screenshot(region=region) if region is not None else screenshot()
        screenshots.append(numpy.array(ss))
        time.sleep(interval)

    # remove duplicate screenshots
    unique_screenshots = []
    for arr in screenshots:
        if not any(numpy.array_equal(arr, unique_arr)
                   for unique_arr in unique_screenshots):
            unique_screenshots.append(arr)

    screenshots = unique_screenshots

    # save screenshots to file
    for i, ss in enumerate(screenshots):
        path = None
        if folder is not None:
            path = join(folder, f'{name}{i}.png') if name is not None else join(folder, f'{i}.png')

        elif name is not None:
            path = f'C:\\Users\\Matt\\Desktop\\inc_pics\\{name}{i}.png'
        else:
            path = f'C:\\Users\\Matt\\Desktop\\inc_pics\\{i}.png'
        Image.fromarray(ss).save(path)


def take_screenshots():

    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\1.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\2.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\3.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\4.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\5.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\6.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\7.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\8.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\9.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\10.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\11.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\12.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\13.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\14.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\15.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\16.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\17.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\18.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\19.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\20.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\21.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\22.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\23.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\24.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\25.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\26.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\27.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\28.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\29.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\30.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\31.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\32.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\33.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\34.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\35.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\36.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\37.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\38.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\39.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\40.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\41.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\42.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\43.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\44.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\45.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\46.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\47.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\48.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\49.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\50.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\51.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\52.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\53.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\54.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\55.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\56.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\57.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\58.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\59.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\60.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\61.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\62.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\63.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\64.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\65.png')
    time.sleep(0.05)
    ss = screenshot(region=(46, 499, 10, 8))
    ss.save(r'C:\Users\Matt\Desktop\inc_pics\66.png')
    time.sleep(0.05)
