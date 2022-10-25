import st7789
import tft_config
import vga1_8x16 as font1
import vga1_16x32 as font2
import utime, math
from machine import Pin, SPI

class TDisplay:
    """
    T-Display ESP32 initialization and convenience handlers
    """
    def __init__(self):
        self.tft = tft_config.config(0)
        self.tft.rotation(1)
        self.tft.init()
        
    def typeset(self, text, coffset=0, loffset=0, font=font1, fg=st7789.WHITE, bg=st7789.BLACK):
        length = len(text)
        col = coffset*font.WIDTH
        line = loffset*font.HEIGHT
        for char in text:
            if (col < self.tft.width()) and (line < self.tft.height()):
                self.tft.text(
                    font,
                    char,
                    col, line,
                    fg, bg)
            col += font.WIDTH
            if (col > self.tft.width() - font.WIDTH) or (char == '\n'):
                col = 0
                line += font.HEIGHT
                
    def typesetlist(self, iterable, font=font1):
        offset = 0
        for f in iterable:
            self.typeset(f, loffset=offset, font=font)
            offset += 1

    def clear(self, bg=st7789.BLACK):
        self.tft.fill(bg)

    # Maximum characters that fit on the display
    def maxchars(self, font=font1):
        return math.floor(self.tft.width() / font.WIDTH) * math.floor(self.tft.height() / font.HEIGHT)


class Button:
    """
    Debounced pin handler
    Modifed from https://gist.github.com/jedie/8564e62b0b8349ff9051d7c5a1312ed7
    """
    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING, debounce=350):
        self.callback = callback
        self.debounce = debounce
        self._next_call = utime.ticks_ms() + self.debounce
        pin.irq(trigger=trigger, handler=self.debounce_handler)

    def call_callback(self, pin):
        self.callback(pin)

    def debounce_handler(self, pin):
        if utime.ticks_ms() > self._next_call:
            self._next_call = utime.ticks_ms() + self.debounce
            self.call_callback(pin)
