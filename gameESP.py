# gameESP.py
# for ESP32
# from https://github.com/cheungbx/gameESP-micropython
#
# gameESP-micropython
# Simple MicroPython game modules and sample games for ESP8266 and ESP32
#
# gameESP.py for esp8266 or esp32
# Use mpy-cross to compile to gameESP.mpy
#
# common micropython module for ESP8266 game board designed by Billy Cheung (c) 2019 08 31
# --usage--
# Using this common micropython game module, you can write micropython games to run
# either on the SPI OLED or I2C OLED without chaning a line of code.
# You only need to set the following line in gameESP.py file at the __init__ function
#        self.useSPI = True  # for SPI display , with buttons read through ADC
#        self.useSPI = False  # for I2C display, and individual hard buttons
#
# Note:  esp8266 is very bad at running .py micropython source code files
# with its very limited CPU onboard memory of 32K
# so to run any program with > 300 lines of micropython codes combined (including all modules),
# you need to convert source files into byte code first to avoid running out of memory.
# Install a version of the  mpy-cross micropython pre-compiler that can run in your system (available from github).
# Type this command to convert gameESP.py to the byte code file gameESP.mpy  using mpy-cross.
#        mpy-cross gameESP.py
# then copy the gameESP.mpy file to the micropython's import directory on the flash
# create your game and leaverge the functions to display, read buttons and paddle and make sounds
# from the gameESP class module.
# Add this line to your micropython game source code (examples attached, e.g. invader.py)
#       from gameESP import gameESP, Rect
#       g=gameESP()
#
#
#
#==================================================================================
# ESP32 Game board
# -----------------
# The pin layout is exactly the same as that of the Odroid-Go
# so this library can be used on the micropython firmware of the Odroid-Go
#
#------------------------
# ESP32 OLED SPI SSD1306
# ==============
# VCC     -  3.3V
# GND     -  GND
# D0/SCK  -  IO18-VSPI-SCK
# D1/MOSI -  IO23-VSPI-MOSI
# RES     -  IO4 for ESP32
# DC      -  IO21
# CS      -  IO5-VSPI CS0
# LED/BLK -  IO14
#
# MISO    -  IO19-VSPI-MISO (not required for OLED)
#
#
# TF Card Odroid-go (optional)
# ================
# CS -    IO22 VSPI CS1
# MOSI -  IO23 VSPI MOSI
# MISO -  IO19 VSPI SCK
# SCK -   IO18 VSPI MISO
#
# ESP32 OLED I2C SSD1306
# ================
# VCC  -  3.3V
# GND   - GND
# SCL -   IO 22
# SDA     IO 21

# Audio
# ======
# Speaker- - GND
# Speaker+ - 10K VR- IO26

# Paddle (10K VR)
# ======
# left   GND
# middle VN/IO39
# right  VCC


# D-PAD Buttons
# =============
# tie one end to 3V3
# UP        IO35-10K-GND
# Down-10K  IO35
# Left      IO34-10K-GND
# Right-10K IO34

# Other Buttons
# ============
# tie one end to GND
# Menu      IO13
# Volume    IO00-10K-3v3
# Select    IO27
# Start     IO39(VN)-10K-3v3
# B         IO33
# A         IO32
#
#-----------------------------------------
import utime
from utime import sleep_ms, ticks_ms, ticks_us, ticks_diff
from machine import Pin, SPI, I2C, PWM, ADC, Timer
from random import getrandbits, seed
import st7789
import tft_config
import vga1_8x16 as font

# MicroPython SSD1306 OLED driver, I2C and SPI interfaces

from micropython import const
import framebuf


# register definitions
SET_CONTRAST        = const(0x81)
SET_ENTIRE_ON       = const(0xa4)
SET_NORM_INV        = const(0xa6)
SET_DISP            = const(0xae)
SET_MEM_ADDR        = const(0x20)
SET_COL_ADDR        = const(0x21)
SET_PAGE_ADDR       = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP       = const(0xa0)
SET_MUX_RATIO       = const(0xa8)
SET_COM_OUT_DIR     = const(0xc0)
SET_DISP_OFFSET     = const(0xd3)
SET_COM_PIN_CFG     = const(0xda)
SET_DISP_CLK_DIV    = const(0xd5)
SET_PRECHARGE       = const(0xd9)
SET_VCOM_DESEL      = const(0xdb)
SET_CHARGE_PUMP     = const(0x8d)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00, # off
            # address setting
            SET_MEM_ADDR, 0x00, # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01, # column addr 127 mapped to SEG0
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08, # scan from COM[N] to COM0
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE, 0x22 if self.external_vcc else 0xf1,
            SET_VCOM_DESEL, 0x30, # 0.83*Vcc
            # display
            SET_CONTRAST, 0xff, # maximum
            SET_ENTIRE_ON, # output follows RAM contents
            SET_NORM_INV, # not inverted
            # charge pump
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01): # on
            self.write_cmd(cmd)
        self.fill(0)
        # self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width == 64:
            # displays with width of 64 pixels are shifted by 32
            x0 += 32
            x1 += 32
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3c, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b'\x40', None] # Co=0, D/C#=1
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80 # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        import time
        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)

class gameESP():
    max_vol = 6
    # duty={0:0,1:0.05,2:0.1,3:0.5,4:1,5:2,6:70}
    duty={0:0,1:1,2:3,3:5,4:10,5:70,6:512}
    tones = {
        ' ': 0,   # silence note
        'c3': 131,
        'd3': 147,
        'e3': 165,
        'f3': 175,
        'f#3': 185,
        'g3': 196,
        'g#3': 208,
        'a3': 220,
        "a#3": 233,
        'b3': 247,
        'c4': 262,
        'd4': 294,
        'e4': 330,
        'f4': 349,
        'f#4': 370,
        'g4': 392,
        'g#4': 415,
        'a4': 440,
        "a#4": 466,
        'b4': 494,
        'c5': 523,
        'c#5': 554,
        'd5': 587,
        'd#5': 622,
        'e5': 659,
        'f5': 698,
        'f#5': 740,
        'g5': 784,
        'g#5': 831,
        'a5': 880,
        'b5': 988,
# note the following can only be played by ESP32, as ESP8266 can play up to 1000Hz only.
        'c6': 1047,
        'c#6': 1109,
        'd6': 1175
    }

    def __init__(self, rotation=1):
        # True =  SPI display, False = I2C display
        self.ESP32 = True
        self.paddle2 = False
        self.useSPI = True
        self.timer = 0
        self.vol = int(self.max_vol/2) + 1
        seed(ticks_us())
        # self.btnU = 1 << 1
        # self.btnL = 1 << 2
        # self.btnR = 1 << 3
        # self.btnD = 1 << 4
        self.btnA = 1 << 1
        self.btnB = 1 << 2
#         self.btnUval = 0
#         self.btnDval = 0
#         self.btnLval = 0
#         self.btnRval = 0
        self.btnAval = 0
        self.btnBval = 0
        self.frameRate = 30
        self.screenW = 240
        self.screenH = 135
        self.Btns = 0
        self.lastBtns = 0

        self.maxBgm = 1
        self.bgm = 1
        self.songIndex = 0
        self.songStart = -1
        self.songEnd   = -1
        self.songLoop  = -3
        self.silence  = 0
        self.songSpeed = 1
        self.timeunit = 1
        self.notes = False
        self.songBuf = []
        self.PinBuzzer = Pin(26, Pin.OUT)
        self.beeper = PWM(self.PinBuzzer, freq=500, duty=0)
        self.beeper2 = PWM(self.PinBuzzer, freq=500, duty=0)        
        self.timerInitialized = False

        # configure oled display SPI ST7789
        self.spi = SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19))
        self.display = tft_config.config(0)
        self.display.rotation(rotation)
        self.display.init()

        self.PinBtnA  = Pin(0, Pin.IN, Pin.PULL_UP)
        self.PinBtnB  = Pin(35, Pin.IN, Pin.PULL_UP)
        # self.adcX = ADC(34)
        # self.adcY = ADC(35)
        self.adc = ADC(Pin(12))
        # self.adcX.atten(ADC.ATTN_11DB)
        # self.adcY.atten(ADC.ATTN_11DB)
        self.adc.atten(ADC.ATTN_11DB)


    def deinit(self) :
      self.beeper.deinit()
      self.beeper2.deinit()
      self.adc.deinit()
      # self.adcX.deinit()
      # self.adcY.deinit()
      if self.useSPI :
        self.spi.deinit()
      if self.timerInitialized :
          self.timer.deinit()

    def getPaddle (self) :
      # ESP32 - 142 to 3155
      return max ( min (int (self.adc.read() / 2.935) - 48, 1023),0)

    def pressed (self,btn) :
      return (self.Btns & btn)

    def justPressed (self,btn) :
      return (self.Btns & btn) and not (self.lastBtns & btn)

    def justReleased (self,btn) :
      return (self.lastBtns & btn) and not (self.Btns & btn)

    def getBtn(self) :

        self.btnAval = not self.PinBtnA.value()
        self.btnBval = not self.PinBtnB.value()

#         val = self.adcX.read()
#         self.btnLval = 1 if val > 2500  else 0
#         self.btnRval = 1 if 1500 < val < 2000 else 0
# 
#         val = self.adcY.read()
#         self.btnUval = 1 if val > 2500  else 0
#         self.btnDval = 1 if 1500 < val < 2000 else 0

        self.lastBtns = self.Btns
        self.Btns = 0
        # self.Btns = self.Btns | self.btnUval << 1 | self.btnLval << 2 | self.btnRval << 3 | self.btnDval << 4 | self.btnAval << 5 | self.btnBval << 6
        self.Btns = self.Btns | self.btnAval << 1 | self.btnBval << 2
        return self.Btns
        print (self.Btns)

    def setVol(self) :
        if self.pressed(self.btnB):
            if self.justPressed(self.btnB) :
                self.vol= min (self.vol+1, self.max_vol)
                self.playTone('c4', 100)
                return True
            elif self.justPressed(self.btnA) :
                self.vol= max (self.vol-1, 0)
                self.playTone('d4', 100)
                return True

        return False
    
    def setFrameRate(self) :
        if self.justPressed(self.btnB) :
            self.frameRate = self.frameRate + 5 if self.frameRate < 120 else 5
            self.playTone('e4', 100)
            return True
        elif self.pressed(self.btnA) :
            self.frameRate = self.frameRate - 5 if self.frameRate > 5 else 120
            self.playTone('f4', 100)
            return True
        return False

    def playTone(self, tone, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq=self.tones[tone], duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def playSound(self, freq, tone_duration, rest_duration=0):
        beeper = PWM(self.PinBuzzer, freq, duty=self.duty[self.vol])
        sleep_ms(tone_duration)
        beeper.deinit()
        sleep_ms(rest_duration)

    def handleInterrupt(self, timer):
        self.beeper2.deinit() # note has been played long enough, now stop sound

        if self.songBuf[self.songIndex] == self.songLoop :
            self.songIndex = 3 # repeat from first note

        if self.songBuf[self.songIndex] != self.songEnd :
            if self.songBuf[self.songIndex] == 0 :
                self.beeper2 = PWM(self.PinBuzzer, freq=100, duty=0)
            elif self.notes :
                self.beeper2 = PWM(self.PinBuzzer, freq=self.tones[self.songBuf[self.songIndex]], duty=self.duty[self.vol])
            else :
                self.beeper2 = PWM(self.PinBuzzer, freq=self.songBuf[self.songIndex], duty=self.duty[self.vol])
            self.timer.init(period=int(self.songBuf[self.songIndex+1] * self.timeunit * self.songSpeed), mode=Timer.ONE_SHOT, callback=self.handleInterrupt)
            self.songIndex +=2

    def startSong(self, songBuf=None):
        if self.bgm :
            if songBuf != None :
                self.songBuf = songBuf
            if self.songBuf[0] != self.songStart :
                print ("Cannot start Song, Invalid songBuf")
                return False
            self.notes = self.songBuf[1]
            self.timeunit = self.songBuf[2]
            self.songIndex = 3
            if not self.timerInitialized :
                self.timerInitialized = True
                self.timer = Timer(1)
            self.timer.init(period=100, mode=Timer.ONE_SHOT, callback=self.handleInterrupt)

    def stopSong(self):
        self.songIndex = 0


    def random (self, x, y) :
        return  getrandbits(20) % (y-x+1) + x

    def display_and_wait(self) :
        # self.display.show()
        timer_dif = int(1000/self.frameRate) - ticks_diff(ticks_ms(), self.timer)
        if timer_dif > 0 :
            sleep_ms(timer_dif)
        self.timer=ticks_ms()


class Rect (object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


    def move (self, vx, vy) :
        self.x = self.x + vx
        self.y = self.y + vy


    def colliderect (self, rect1) :
      if (self.x + self.w   > rect1.x and
        self.x < rect1.x + rect1.w  and
        self.y + self.h > rect1.y and
        self.y < rect1.y + rect1.h) :
        return True
      else:
        return False