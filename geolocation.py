import coordinates
import collections
import math
import gps_nmea
from tuples import Tuples
import time


# Yonsei Shinchon main gate
CENTER_LATITUDE=37.560179
CENTER_LONGITUDE=126.936925

EARTH_RADIUS=6400*1000
METER_PER_LATITUDE=2*math.pi*EARTH_RADIUS/360
HORIZ_SMALLCIRC_R=math.cos(math.radians(CENTER_LATITUDE))*EARTH_RADIUS
METER_PER_LONGITUDE=2*math.pi*HORIZ_SMALLCIRC_R/360

# coordinates, cartesian, centered on a point
# Here we approximate the earth's surface as a plane.
# we also assume the earth is a perfect sphere
# W - <-- X --> + E (Longitude)
# S - <-- Y --> + N (Latitude)
# Z = Altitude
class LocalGroundCoordinates:
	def __init__(self,*,x,y,z):
		self._x=x
		self._y=y
		self._z=z
	@property
	def x(self):
		return self._x
	@property
	def y(self):
		return self._y
	@property
	def z(self):
		return self._z
	
	@classmethod
	def from_lla(cls,*,longitude,latitude,altitude):
		rlat=latitude-CENTER_LATITUDE
		rlon=longitude-CENTER_LONGITUDE
		return cls(
			x=rlon*METER_PER_LONGITUDE,
			y=rlat*METER_PER_LATITUDE,
			z=altitude)
	@classmethod
	def from_GD(cls,gd):
		return cls.from_lla(
			longitude=gd.longitude,
			latitude=gd.latitude,
			altitude=gd.altitude)
	def to_tuple(self):
		return (self.x,self.y,self.z)
	def __str__(self):
		return F"LGC[X{self.x:+8.1f}m / Y{self.y:+8.1f}m / Z{self.z:+8.1f}m]"
		
class PositionSolver:
	'''
	Interpolates ~1update/second GPS data to contineous location data
	...that's the idea anyway
	'''
	def __init__(self,gps:gps_nmea.NmeaGPS):
		self._gps=gps
		gps.add_listener(self._gps_callback)
		self._gd_history=[]
		self._gdhist_maxlen=100 #entries
		self._gdhist_maxtime=10 #sec
	def _prune_history(self):
		t=time.time()
		while True:
			if not self._gd_history: #Empty
				break
			elif len(self._gd_history)>self._gdhist_maxlen: 
				# Too long
				del self._gd_history[0]
			elif self._gd_history[0].time_system<t-self._gdhist_maxtime:
				# Too old
				del self._gd_history[0]
			else: #OK
				break
		
	def _gps_callback(self,gd:gps_nmea.GPSData):
		if gd.has_fix:
			#print("New fix:",gd)
			self._gd_history.append(gd)
			self._prune_history()
	def get_location(self):
		self._prune_history()
		if self._gd_history:
			return LocalGroundCoordinates.from_GD(self._gd_history[-1])
		else:
			return None
	def get_velocity(self):
		self._prune_history()
		vel=None
		try:
			#print("Vel",self._gd_history[-1])
			gd1=self._gd_history[-2]
			gd2=self._gd_history[-1]
			p1=LocalGroundCoordinates.from_GD(gd1).to_tuple()
			p2=LocalGroundCoordinates.from_GD(gd2).to_tuple()
			#print(p1)
			#print(p2)
			deltaP=Tuples.sub(p2,p1)
			#print(deltaP)
			deltaT=(gd2.time_system-gd1.time_system)
			#print(deltaT)
			vel=Tuples.div(deltaP,deltaT)
			#print(vel)
		except IndexError: # Not enough history
			pass
		except TypeError: # Operations on None
			pass
		except AttributeError: #Dereferencing None
			pass
		return vel
	
if __name__=="__main__":
	
	ng=gps_nmea.NmeaGPS(playback_json="gps_2023-05-20_aptbike.json")
	ng.start()
	ps=PositionSolver(ng)
	
