"""
emoticon mood pendant using large chango_64 font
"""

import utime, gc
import st7789
import button2
import chango_64 as font
from machine import Pin

TMOMAGENTA = 0xE00E

emoticons = [
    ':-]',
    ':-?',
    ':-)',
    ':-D',
    ':-|',
    ':-O',
    ':-('
    ]

colors = [
    TMOMAGENTA,
    st7789.WHITE,
    st7789.RED,
    st7789.MAGENTA,
    st7789.YELLOW,
    st7789.CYAN,
    st7789.GREEN,
    st7789.BLUE
    ]

changed = 1
colored = 0

def nextEmoticon(button):
    global changed
    changed = 1
    
def prevEmoticon(button):
    global changed
    changed = -1
    
def nextColor(button):
    global colored
    colored = 1
    
def prevColor(button):
    global colored
    colored = -1
    
btn1 = button2.Button2(0)
btn1.setClickHandler(nextColor)
btn1.setDoubleClickHandler(prevColor)

btn2 = button2.Button2(35)
btn2.setClickHandler(nextEmoticon)
btn2.setDoubleClickHandler(prevEmoticon)

def display_emote(text, color):
    TD.tft.rotation(3)
    TD.tft.fill(st7789.BLACK)
    column = 64
    row = 32

    # Print one character at a time
    for char in text:
        width = TD.tft.write_len(font, char)       # get the width of the character
        TD.tft.write(
            font,
            char,
            column,
            row,
            color,
            st7789.BLACK)

        column += width

def main():
    global changed, colored
    
    timer = 0
    i = 0
    j = 0
    while True:
        btn1.loop()
        btn2.loop()
        if changed or colored:
            if (changed != 0):
                i = (i + changed) % len(emoticons)
            if (colored != 0):
                j = (j + colored) % len(colors)
            display_emote(emoticons[i], colors[j])
            changed = 0
            colored = 0
            timer = 0
        TD.tft.rotation(2)
        TD.typeset("{} felt".format(userpronoun['xe']))
        TD.typeset("for %.1f s" % timer, 0, 14)
        utime.sleep(0.1)
        timer += 0.1

main()