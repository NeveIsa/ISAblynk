try:
	import ISAblynk
except:
	import ESPblynk as ISAblynk

def callback(data):
		print ("Got : ",data)



import json

with open("config.json") as f:
	conf = json.loads(f.read().strip())

TOKEN = conf["TOKEN"]

print("TOKEN:%s " % TOKEN)
ISAblynk.setup(TOKEN,callback)
