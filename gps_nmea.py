import io
import pynmea2
import serial
import time
import datetime
import collections
import gps_record
import threading

# RMC basic
# VTG track
# GGA location+alt+sats <<<
# GSA satallite codes
# GSV sat snr/locations
# GLL location

GPSData=collections.namedtuple( #GGA
	"GPSData",
	["time_system","time_gps",
	 "satellites","precision","quality",
	 "latitude","longitude","altitude",
	 "has_fix"])
LLA = collections.namedtuple(
	"LLA",
	["latitude","longitude","altitude"])



class NmeaGPS(threading.Thread):
	def __init__(self,*args,serial_port=None,playback_json=None,**kwargs):
		super().__init__(*args,**kwargs)
		if serial_port is not None:
			self._ser = serial.Serial(serial_port, 9600, timeout=0)
		elif playback_json is not None:
			self._ser=gps_record.FakeSerial(playback_json)
		else:
			0/0
		self._alive=True
		self._listeners=[]
	def add_listener(self,f):
		self._listeners.append(f)
	def notify_callbacks(self,gd):
		#print("CB call")
		for i in self._listeners:
			i(gd)
	def die(self):
		self._alive=False
	def run(self):
		while self._alive:
			try:
				line = self._ser.readline()
				#print(repr(line))
				if not line:
					time.sleep(0.01)
					continue
				msg = pynmea2.parse(line.decode())
				
				#print(msg)
				#print(time.time())
				#print("  Talker ",msg.talker)
				#print("  Type   ",msg.sentence_type)
				#print("  Data:  ",msg.data)
				if msg.sentence_type=="GGA":
					'''
					print(datetime.datetime.now().strftime("%H:%M:%S"))
					print("    Time      ", msg.timestamp)
					print("    Latitude  ", msg.lat)
					print("    LatDir    ", msg.lat_dir)
					print("    Longitude ", msg.lon)
					print("    LonDir    ", msg.lon_dir)
					print("    Quality   ", msg.gps_qual)
					print("    #Sats     ", msg.num_sats)
					print("    Accuracy  ", msg.horizontal_dil)
					print("    Altitude  ", msg.altitude)
					print("    AltUnit   ", msg.altitude_units)
					'''
					lat=None
					lon=None
					alt=None
					fix=False
					try:
						lat=float(msg.latitude)
						lon=float(msg.longitude)
						alt=float(msg.altitude)
						fix=True
					except ValueError:
						pass
					except TypeError:
						pass
					
					gd=GPSData(
						time_system=time.time(),
						time_gps=msg.timestamp,
						satellites=msg.num_sats,
						precision=msg.horizontal_dil,
						quality=msg.gps_qual,
						latitude=lat,
						longitude=lon,
						altitude=alt,
						has_fix=fix)
					#print(gd)
					self.notify_callbacks(gd)
					
					
			except serial.SerialException as e:
				print('Device error: {}'.format(e))
				break
			except pynmea2.ParseError as e:
				print('Parse error: {}'.format(e))
				continue



	
