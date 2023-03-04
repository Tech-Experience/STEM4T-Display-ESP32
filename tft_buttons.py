
# input pins for buttons: you will need to change these to match your wiring

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "t-display"
        self.left = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
        self.right = Pin(35, mode=Pin.IN, pull=Pin.PULL_UP)
        
        self.a = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(13, mode=Pin.IN, pull=Pin.PULL_UP)