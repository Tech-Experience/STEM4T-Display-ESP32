"""
photos.py

    Displays contents of a folder

    Derived from https://github.com/russhughes/st7789_mpy/tree/master/examples/clock

    Background images courtesy of the NASA image and video gallery available at
    https://images.nasa.gov/

"""
import gc, os, utime
from machine import Pin, SPI
import st7789
import tft_config, tft_typeset

tft = tft_config.config(1)

timeout = 0

def cycle(p):
    """return the next item in a list"""
    try:
        len(p)
    except TypeError:
        cache = []
        for i in p:
            yield i
            cache.append(i)

        p = cache
    while p:
        yield from p

def last_btn(pin):
    global timeout
    print('prev')
    timeout = 0

def next_btn(pin):
    global timeout
    print('next')
    timeout = 0

def main():
    """
    Initialize the display and show the time
    """

    tft.init()

    backgrounds = cycle(os.listdir("./nasa_{}x{}/".format(tft.width(), tft.height())))

    btn1 = tft_typeset.Button(pin=Pin(0, mode=Pin.IN, pull=Pin.PULL_UP), callback=next_btn)
    btn2 = tft_typeset.Button(pin=Pin(35, mode=Pin.IN, pull=Pin.PULL_UP), callback=last_btn)

    while True:
        global timeout, background_change
        if timeout < 0:
            timeout = 10
            image = next(backgrounds)
            print(image)
            gc.collect()

            # draw the new background from the nasa_{WIDTH}x{HEIGHT} directory
            image_file = "nasa_{}x{}/{}".format(tft.width(), tft.height(), image)
            tft.jpg(image_file, 0, 0, st7789.SLOW)

        utime.sleep(0.5)
        timeout -= 1

main()

