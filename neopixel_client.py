try:
	import ISAblynk
except:
	import ESPblynk as ISAblynk


from machine import Pin
from neopixel import NeoPixel

import time

pin = Pin(15, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
np = NeoPixel(pin, 8)   # create NeoPixel driver on GPIO0 for 8 pixels

red=0
green=0
blue=0

def glow(r,g,b):
	for i in range(8):
		np[i]=(r,g,b)
	np.write()
	print("writing colors:",r,g,b)



def callback(data):
		print ("Color : ",data)
		global red
		global green
		global blue
		#red,green,blue=0,0,0
		if data[0]=='vw':
			value=int(int(data[2])/4) #scale 1024 to 256
			if data[1]=='1':
				#print('red')
				red=value
			elif data[1]=='2':
				#print('green')
				green=value
			elif data[1]=='3':
				#print('blue')
				blue=value
			glow(red,green,blue)



glow(100,0,0)
time.sleep_ms(500)
glow(0,100,0)
time.sleep_ms(500)
glow(0,0,100)
time.sleep_ms(500)
glow(0,0,0)

# Wait for wifi
glow(250,100,150)


glow(0,0,100)
time.sleep_ms(700)
glow(250,100,150)



TOKEN=join_network.config["TOKEN"]
ISAblynk.setup(TOKEN,callback)
