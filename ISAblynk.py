import socket,time,sys

class MSGTYPE:
	RSP    = 0
	LOGIN  = 2
	PING   = 6
	BRIDGE = 15
	HW     = 20
	CONNECT_REDIRECT = 41

class MSGSTATUS:
	OK = 200
	INVALID_TOKEN=9

class blynkDevice:
	server='blynk-cloud.com'
	server='188.166.206.43'
	port=8442
	#port=80
	sock=None
	token=None
	msgID=0

	connected=False

	def __init__(self,token):
        	self.token = token

	def connect(self):
		self.msgID=0
		try:
			try:
				#raise
				self.sock=socket.create_connection((self.server,self.port),timeout=10)
			except Exception as e:
				print ("Exception using socket.create_connection...",e)
				print ("Falling back to lower level socket methods...")
				self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				self.sock.connect(socket.getaddrinfo(self.server,self.port)[0][-1])
			if self.sock:
				print ("Connected...")
				return True
			else:
				print ("Could not connect to server...")
				self.connected=False
				return False
		except Exception as e:
			print ("Exception in connecting to server",e)
			self.connected=False

	def frame(self,msgtype,msg,msgID=None):
		if not msgID:
			self.msgID = self.msgID+1
			msgID=self.msgID
		msglen = len(msg)
		#print(f"msgtype:{msgtype} | msgID:{msgID} | msg:{msg}")
		payload = chr(msgtype) + chr(msgID//256) + chr(msgID%256) + chr(msglen//256) + chr(msglen%256)
		payload = payload + msg
		#print payload
		return payload

	def deframe(self,payload):
		if len(payload)<5:
			print ("deframe payload header is less than 5 bytes..error")
			return (0,0,0)
		try:
			msgtype=payload[0]
			msgID=payload[1]*256 + payload[2]
			msglen=payload[3]*256 + payload[4]
			return (msgtype,msgID,msglen)
		except Exception as e:
			print ("deframe exception ->",e)
			return (0,0,0)


	def tx(self,payload):
		try:
			self.sock.sendall(payload.encode())
		except Exception as e:
			print ("exception in tx ->",e)
			self.connected=False

	def rx(self,length):
		rcv = b""
		l=0
		try:
			while True:
				r = self.sock.recv(length-l)
				#print(type(r))
				#print(r+r)
				rcv = rcv + r
				l = len(rcv)
				if l<length:
					pass
				else:
					break
		except socket.timeout:
			rcv=b""
		except Exception as e:
			print ("rx exception ->",e)
			rcv=b""
			self.connected=False
		#print(rcv)
		return rcv

	def rxFrame(self):
		response = self.rx(5)
		if not response:
			return None,None
		response=self.deframe(response)
		data=self.rx(response[-1]) #response[-1] contains the data
		payload=self.frame(MSGTYPE.RSP,"",msgID=response[1]) #ACK back
		self.tx(payload)
		return response,data


	def auth(self):

		payload=self.frame(MSGTYPE.LOGIN,self.token)

		try:
			self.tx(payload)
			response = self.rx(5)
			response=self.deframe(response)
			if response[0]==MSGTYPE.CONNECT_REDIRECT:
				print ("CONNECT_REDIRECT command received...")
				length_of_msg = response[2]
				msg=self.rx(length_of_msg)
				new_ip,new_port = msg.split("\0")
				print ("=== New IP : new Port -> %s : %s ===" % (new_ip,new_port))
				self.server,self.port = new_ip,new_port #update with new IP and Port
				print ("New IP and Port set. Next attempt to connect will use new settings...")
				self.connected=False
				return False
			if response[-1]==MSGSTATUS.INVALID_TOKEN:
				print("Invalid TOKEN: %s" % self.token)
				exit()

			if response[-1]==MSGSTATUS.OK:
				print ("Authenticated...")
				self.connected=True
				return True
			else:
				print ("Authentication failed")
				print ("response ->",response)
				self.connected=False
				return False

		except Exception as e:
			print ("Auth exception",e)
			self.connected=False
			return False

	def ping(self):
		payload = self.frame(MSGTYPE.PING,"")
		print ("Ping...")
		self.tx(payload)
		response = self.rx(5)
		response = self.deframe(response)
		if not response:
			print ("Ping failed...")
			self.connected=False
		if response==(MSGTYPE.RSP,self.msgID,MSGSTATUS.OK):
			print ("...Pong",self.msgID)


	def unpack_command(self,cmd):
		#print (cmd)
		#print(len(cmd))
		#print(cmd[0],cmd[1],cmd[2],cmd[3])
		cmd=cmd.decode("ascii")
		cmd = cmd.split("\0") #split into
		pinCmdType=cmd.pop(0)
		if pinCmdType=="pm":
			pass # no values to pop if 'pm' command
			return (pinCmdType,None,None)
		pinNo=cmd.pop(0)
		pinValue=cmd.pop(0)
		return (pinCmdType,pinNo,pinValue)


	def manage(self,callback=None):
		try:
			if not self.connected:
				print ("(Re)connecting...")
				return self.connect() and self.auth()
			else:
				response,data=self.rxFrame()
				#print response,data
				#return
				#print response,data
				if response:
					if not callback:
						print (response)
				else:
					self.ping()
					return False

				if response[0]==MSGTYPE.HW or response[0]==MSGTYPE.BRIDGE:
					pass
				else:
					print ("Unknown Message/Command received...")
					return False

				if data:
					result = self.unpack_command(data)
					if(result[0])=="pm":
						print ("Pin Mode Command Received...An APP just connected to this BlynkDevice..")
						return True
					if callback:
						callback(result)
					else:
						print (result)
					return result
				else:
					return False

		except Exception as e:
			print ("Exception in manage ->",e)
			print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))



def setup(token,callback=None):
	dev = blynkDevice(token)
	dev.connect()
	while not dev.auth():
		dev.connect()
		dev.ping()
	
	print ("Delegating to 'manage' method...")

	def myprint(x):
		if callback:
			callback(x)
		else:
			print (x)

	try:
		while 1:
			dev.manage(myprint)
	except KeyboardInterrupt:
		print ("Closing connection...")
		dev.sock.close()
		print ("Graceful shutdown...")




if __name__=="__main__":

	def callback(data):
		print ("Got : ",data)

	import json
	with open("config.json") as f:
		conf = json.loads(f.read())


	TOKEN = conf["TOKEN"]
	setup(TOKEN,callback)

