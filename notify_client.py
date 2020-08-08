import machine
import ssd1306
import network
import terminal
import time
import ujson

import neopixel

import join_network
import ESPblynk as ISAblynk

i2c = machine.I2C(-1, machine.Pin(4), machine.Pin(5))
oled = ssd1306.SSD1306_I2C(128,64, i2c)
term = terminal.Terminal(oled)


class Notify:
    def __init__(self,_terminal):
        self.terminal = _terminal
        self.postboard_linestart = 3 # last 3 lines are used as notifications - i.e lineno 3,4,5
        self.postboard_lineend = 6 # last 3 lines are used as notifications
        self.postboard_linepos = self.postboard_linestart

    def postboard(self,text):
        self.terminal.println(text,self.postboard_linepos)
        #print(self.postboard_linepos)
        self.postboard_linepos+=1
        self.postboard_linepos = self.postboard_linestart + (self.postboard_linepos - self.postboard_linestart) % (self.postboard_lineend - self.postboard_linestart)




class NPled:
    def __init__(self,pin,no_of_leds=8):
        self.pin = pin
        self.nleds=no_of_leds
        self.np = neopixel.NeoPixel(machine.Pin(pin),no_of_leds)

    def glow(self,r=100,g=100,b=100,alpha=1,led_id=None):
        r,g,b = list(map(int,map(lambda c: c * alpha,[r,g,b])))
        list(map(lambda i: self.np.__setitem__(i,(r,g,b)),range(self.nleds))) # this is so chhhhoooooool
        self.np.write()    



def intro(SSID):
    term.clean()
    term.println("ISAblyng V0.1",lineno=0)
    term.println("SSID:"+SSID)
    term.println("IP:" + network.WLAN().ifconfig()[0])
    term.hline(3,solid=True)



### callback
def handle_event(event):
    pinname = event[0]
    pinno =  event[1]
    pin = pinname + pinno

    value = event[2]

    global R,G,B

    if pin=="vw0":
        #value = message notification
        notify.postboard(value)
        print("posted ->",value)

    elif pinname=='vw':
        if pinno == '1':
            R = value
        elif pinno == '2':
            G = value
        elif pinno == '3':
            B = value
        
        print("NeoPixel -> r:%s - g:%s - b:%s" % (R,G,B))
        npled.glow(r=R,g=G,b=B)
    



### MAIN CODE

# read config
with open("config.json") as f:
  config=ujson.loads(f.read())

SSID = config["AP_NAME"]
PASS = config["AP_PASS"]
TOKEN= config["TOKEN"]

intro(SSID)
join_network.join(SSID,PASS)
intro(SSID)

notify = Notify(term)
npled = NPled(config["NEOPIN"])

# set global colors
R,G,B = 0,0,0

ISAblynk.setup(TOKEN,callback=handle_event)
