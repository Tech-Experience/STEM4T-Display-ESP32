# test_button.py

import button2
import utime

def btn1callback(button):
    print('btn1 callback %d' % button.last_click_type )
    TD.typeset('btn1 click type %d' % button.last_click_type, 0, 7 )
    
def btn2callback(button):
    print('btn2 callback %d' % button.last_click_type )
    TD.typeset('btn2 click type %d' % button.last_click_type )

btn1 = button2.Button2(0)
btn1.setClickHandler(btn1callback)
btn1.setDoubleClickHandler(btn1callback)
btn1.setTripleClickHandler(btn1callback)
btn1.setLongClickHandler(btn1callback)

btn2 = button2.Button2(35)
btn2.setClickHandler(btn2callback)
btn2.setDoubleClickHandler(btn2callback)
btn2.setTripleClickHandler(btn2callback)
btn2.setLongClickHandler(btn2callback)


TD.clear()

TD.typeset('Button test', 1, 1, font=tft_typeset.font2)
while True:
    btn1.loop()
    btn2.loop()
    utime.sleep(0.05)