
import collections
import math
import gps_nmea

# coordinates, cartesian, centered on a point
# we assume the earth is a circle - accuracy isn't too important here
# W - <-- X --> + E (Longitude)
# S - <-- Y --> + N (Latitude)
# Z = Altitude

# Yonsei
#CENTER_LATITUDE=37.560179
#CENTER_LONGITUDE=126.936925

# Ecorich
CENTER_LATITUDE=37.456462
CENTER_LONGITUDE=127.013232

EARTH_RADIUS=6400*1000
METER_PER_LATITUDE=2*math.pi*EARTH_RADIUS/360
HORIZ_SMALLCIRC_R=math.cos(math.radians(CENTER_LATITUDE))*EARTH_RADIUS
METER_PER_LONGITUDE=2*math.pi*HORIZ_SMALLCIRC_R/360

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
	def from_GD(cls,gd):
		rlat=gd.latitude-CENTER_LATITUDE
		rlon=gd.longitude-CENTER_LONGITUDE
		return cls(
			x=rlat*METER_PER_LATITUDE,
			y=rlon*METER_PER_LONGITUDE,
			z=gd.altitude)
	def to_LLA(self):
		0/0
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
		self._last_gps_location=None
	def _gps_callback(self,gd:gps_nmea.GPSData):
		if gd.has_fix:
			self._last_gps_location=LocalGroundCoordinates.from_GD(gd)
	def get_location(self):
		return self._last_gps_location
	
