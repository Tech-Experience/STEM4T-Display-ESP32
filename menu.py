import utime, os, gc
import st7789
import tft_typeset
import button2

from machine import Pin, SPI

def btn1handler(pin):
    ms.incr()
    TD.clear()
    TD.typesetlist(ms.listoptions(), font=tft_typeset.font2)
    
def btn2handler(pin): 
    TD.clear(TMOMAGENTA)
    TD.typeset(ms.getselection(), font=tft_typeset.font2)
    cleanupAndLaunch(ms.getselection())

btn1 = button2.Button2(0)
btn2 = button2.Button2(35)

btn1.setTapHandler(btn1handler)
btn2.setTapHandler(btn2handler)

class MenuSelector:
    """
    List of python scripts to run
    """
    def __init__(self, prefilter='_'):
        self.selection=0
        self.options=[o for o in os.listdir() if o.startswith(prefilter)]
    def incr(self):
        self.selection=(self.selection+1) % len(self.options)
    def decr(self):
        self.selection=(self.selection-1) % len(self.options)
    def listoptions(self):
        return self.options[self.selection:]
    def getselection(self):
        return self.options[self.selection]

ms = MenuSelector()

def cleanupAndLaunch(scriptfile):
        print('Script: %s' % scriptfile)
        print('mem_free %.0fkB' % (gc.mem_free() / 1024))
        
#         # Destroy button handler objects
#         btn1 = None
#         btn2 = None
#         btn1handler = None
#         btn2handler = None
#         ms = None
        
        gc.collect()
        exec(open(scriptfile).read())

def main():
    TD.clear()
    TD.typesetlist(ms.listoptions(), font=tft_typeset.font2)
    while True:
        btn1.loop()
        btn2.loop()
        utime.sleep(0.1)

main()