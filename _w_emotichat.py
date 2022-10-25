## Creates a Wifi access point
## Activates an emoticon chat partyline

ap_ssid = 'TDnet'
ap_password = 'FiveGfor4ll'

import network
import utime

server_mode = False

def wifi_connect():
    global server_mode
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(reconnects=0)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ap_ssid, ap_password)
        # Wait 3 seconds for connection to occur
        timeout = 30
        while timeout > 0:
            timeout -= 1
            if wlan.isconnected():
                timeout = 0
            utime.sleep(0.1)
        if not wlan.isconnected():
            print('Network not detected; starting WAP')
            ap = network.WLAN(network.AP_IF)
            ap.active(True)
            ap.config(essid=ap_ssid, password=ap_password, authmode=3)
            server_mode = True
            print('AP server at:', ap.ifconfig())
            return(ap.ifconfig()[0])
    print('network config:', wlan.ifconfig())
    return(wlan.ifconfig()[0])

try:
  import usocket as socket
except:
  import socket

import gc, _thread
import st7789
import vga1_8x16 as font
import button2
from _thread import *

TMOGREY = st7789.color565(128,128,128)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
IP_address = wifi_connect()
Port = int(1001)

server_IP = '192.168.4.1'

TD.clear()
TD.typeset("%s : %d" % (IP_address, Port))
 
server.bind((IP_address, Port))
 
# listen for up to 5 incoming connections at a time
server.listen(5)
 
list_of_clients = []
messagelist = []

 
def broadcast(message, list_of_clients):
    for client in list_of_clients:
        # Don't send messages to myself
        if client == IP_address:
            pass
        print("Send to %s" % client)
        delivery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        delivery.connect((client, Port))
        try:
            delivery.send(message)
        except:
            remove(client)
        delivery.close()

# remove a client that is no longer responding
def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

def send_to_server(message):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((server_IP, Port))
    server.send(message)
    server.close()
    gc.collect()

def connection_loop():
    while True:
        # Display any incoming messages
        conn, addr = server.accept()
        data = conn.read().decode()
        print("Via %s :\n%s" % (addr[0], data))
        TD.typeset("Via %s :" % addr[0], 0, 2, fg=TMOGREY)
        TD.typeset("%s" % data, 0, 3)

        # If we're the server, keep a list of everyone connected
        if server_mode:
            list_of_clients.append(addr[0])
            print (addr[0] + " connected")
            TD.typeset(addr[0] + " connected", 0, 1, fg=TMOGREY)
            # and send any incoming message to everyone else 
            broadcast(data, list_of_clients)
            conn.close()
            
        gc.collect()

 
from machine import Pin

emoticons = [
    ':-]',
    ':-?',
    ':-)',
    ':-D',
    ':-|',
    ':-O',
    ':-('
    ]

changed = 1
sendmsg = 0

def nextEmoticon(button):
    global changed
    changed = 1
    
def prevEmoticon(button):
    global changed
    changed = -1
    
def sendEmoticon(button):
    global sendmsg
    sendmsg = 1
    
btn1 = button2.Button2(0)
btn1.setClickHandler(nextEmoticon)
btn1.setDoubleClickHandler(prevEmoticon)

btn2 = button2.Button2(35)
btn2.setClickHandler(sendEmoticon)
 
 
def main():
    
    # Network loop runs in a separate thread from the GUI loop
    try:
        start_new_thread(connection_loop, ())
    except:
        print('Error: unable to start listening thread')
        TD.typeset('Error: unable to start listening thread', 0, 3)
        
    global changed, sendmsg
    
    i = 0
    # The GUI loop
    while True:
        btn1.loop()
        btn2.loop()
        # Select the next emoticon
        if changed:
            i = (i + changed) % len(emoticons)
            TD.typeset("Send: %s" % emoticons[i], 0, 6, fg=TMOMAGENTA)
            changed = 0

        # Send message to the server
        if sendmsg:
            message = "<%s> %s" % (username, emoticons[i])
            print('Sending %s' % message)
            send_to_server(message)
            sendmsg = 0

        utime.sleep(0.1)
            
    
main()