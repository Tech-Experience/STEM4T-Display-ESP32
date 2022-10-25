import uos, sys, gc, utime
import st7789
import tft_typeset
from machine import Pin, ADC

stats = uos.statvfs('/')
bsize = stats[0]
tot_blocks = stats[2]
free_blocks = stats[3]
used_blocks = tot_blocks - free_blocks

power = ADC(Pin(34))
power.atten(ADC.ATTN_11DB)

def showVoltage():
    vref = 1100
    v = power.read()
    battery_voltage = (v / 4095.0) * 2.0 * 3.3 * (vref / 1000.0)
    return battery_voltage

print('micropython v', uos.uname().release)
print(sys.version)
print('used %.0fkB of %.0fkB'
      % (used_blocks * bsize / 1024, tot_blocks * bsize / 1024))
print('mem_free: %.0fkB'
      % (gc.mem_free() / 1024))
print("voltage: {}V".format(showVoltage()))

TD.clear()
maxchars = TD.maxchars()
TD.typesetlist(sys.version.split())

TD.typeset('used: %.0fkB / %.0fkB'
           % (used_blocks * bsize / 1024, tot_blocks * bsize / 1024),
           loffset=5)
TD.typeset('mem_free: %.0fkB'
           % (gc.mem_free() / 1024),
           loffset=6)
TD.typeset('voltage: %.2fV'
           % showVoltage(),
           loffset=7)

utime.sleep(5)