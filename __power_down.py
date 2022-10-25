import esp32, utime
import st7789
from machine import Pin, PWM, deepsleep
from time import sleep

TD.clear()
TD.typeset("Powering Down", 1, 1, font=tft_typeset.font2, fg=st7789.RED)

wake1 = Pin(35, mode=Pin.IN)
wake2 = Pin(0, mode=Pin.IN)

# Press any button to wake up
esp32.wake_on_ext1(pins = (wake1, wake2), level = esp32.WAKEUP_ALL_LOW)

print('Going to sleep')

fader=PWM(Pin(4))
max_brightness = 512
for i in range(max_brightness, 0, - max_brightness // 10):
    fader.duty(i)
    utime.sleep(0.2)

deepsleep()
