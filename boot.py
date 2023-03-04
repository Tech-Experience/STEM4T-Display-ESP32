# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

# Intended for use with the TTGO T-Display-ESP32 micropython firmware from
# https://github.com/russhughes/st7789_mpy

import utime

# Globally available variables
username = 'Operator'
userpronoun = {
    'xe':  'they',
    'xem': 'them',
    'xir': 'their'
    }
TMOMAGENTA = const(0xE00E)


import tft_typeset
TD = tft_typeset.TDisplay()

TD.typeset("Hello", 4, 1, font=tft_typeset.font2)
TD.typeset(username, 3, 2, font=tft_typeset.font2)
TD.typeset("https://tinyurl.com/iotdisplay", 0, 7, fg=TMOMAGENTA)

# Pause before proceeding to main.py
utime.sleep(1)
