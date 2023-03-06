# STEM4T-Display-ESP32
Companion repository for [MicroPython_for_the_T-Display-ESP32](https://tinyurl.com/iotdisplay) STEM learning module
---
micropython samples for TTGO T-Display ESP32 device companion for STEM learning module

Mostly based on the examples from: 
* https://github.com/russhughes/st7789_mpy 
* https://github.com/cheungbx/gameESP-micropython

and other sources as noted with adaptations for the 2-button T-Display hardware
* https://github.com/Xinyuan-LilyGO/TTGO-T-Display



boot.py  :  runs on every reset, global variables

main.py  :  runs after a normal reset.  In this case, it calls menu.py, (but this can be replaced by another script)

menu.py  :  Launch any script that starts with an underscore '_'.  Button 1 scrolls down, Button 2 launches top script.

__power_down.py : Puts device in low power state.

_feathers.py : pretty colors demo.

_fortunate.py : Connects to the public 'tmobile' wifi available at stores and displays a random quote from the internet.

_fortune.py : displays a random quote from a local list.

_g_breakout.py : brickbreaker port.  Use button 2 to select an AI

_g_pong.py : pong game.  Use button 2 to choose control of one or both paddles, or see AI vs. AI

_g_roids.py : asteroids game.  Press both buttons to activate thrusters.

_g_snake.py : eat the apples.  Use button 2 to select an AI 

_g_tet.py : working version of Tetris ported from https://github.com/VolosR/TTGOTetris/blob/main/TTgOTetris.ino .  But no music (yet)

_g_tetris.py : Non-functional Tetris demo - I broke some game logic while upscaling it for the T-Display.  However, it plays music if you connect a small speaker to pin 26 and GND, so I kept it.  Button 2 selects music on Tetris menu.

_mood.py : emoticon display.

_photos.py : displays any 240x135 .jpg photos you uploaded into photos_240x135 directory using the ampy utility.

_photos_nasa.py : displays photos in the nasa_240x135 directory. I removed the clock from Russ Hughes's example so it wouldn't require wifi networking.

_rolldice.py : D6 roll

_sysinfo.py : Display MicroPython version, available flash and heap memory, and battery / USB power voltage

_test_button.py : Shows single, double, triple, and long click events

_w_emotichat.py : First device creates a simple chat client for subsequent devices to connect to.  Button 1 chooses an emoticon to send, button 2 sends it.  Unfortunately, a threading bug on the first (server) device stops everything if it sends more than one message, but all the other client devices can share emoticons to their hearts' content.

_web_server.py : creates a WiFi access point that serves a simple web page.  Connect a phone or computer to the wifi access point and visit http://192.168.4.1/ to view a random fortune.
