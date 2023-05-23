import serial
import time
import json
import ansi

class FakeSerial:
	def __init__(self,jsonpath):
		with open(jsonpath,"r") as f:
			self._data=json.load(f)
		self._time_start=time.time()
	def readline(self):
		t=time.time()-self._time_start
		if not self._data:
			return None
		if self._data[0][0]>t:
			return None
		
		res=self._data[0][1]
		del self._data[0]
		return res.encode()
	
		
if __name__=="__main__":
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)

	data=[]
	startT=time.time()
	while 1:
		try:
			line = ser.readline()
			#print(repr(line))
			if not line:
				time.sleep(0.01)
				continue
			t=time.time()-startT
			line=line.decode()
			data.append((t,line))
			
			print(line.strip())

			if line.startswith("$GPGGA"):
				ls=line.strip().split(",")
				print("  "+ansi.BOLD+ansi.GREEN+F"#Sats {ls[7]} | Precision {ls[8]} | Lat {ls[2]} | Lon {ls[4]}"+ansi.RESET)
				
				
		except serial.SerialException as e:
			print('Device error: {}'.format(e))
			break
		except KeyboardInterrupt:
			print("Break!")
			break

	print("Save...")
	with open("gsc3.json","w") as f:
		#print(data)
		#print(f)
		json.dump(data,f,indent=2)
	print("Saved!")
