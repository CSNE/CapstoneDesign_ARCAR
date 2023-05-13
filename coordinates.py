# Code relating to coordinates and conversions
import collections

# This is for my sanity, since we're dealing with both 
# (y,x) (OpenCV) and (x,y) (PIL) conventions here
Coordinates2D = collections.namedtuple(
	"Coordinates2D",
	["x","y"])
Point3D = collections.namedtuple(
	"Point3D",
	["x","y","z"])
BoundingBox = collections.namedtuple(
	"BoundingBox",
	["xmin","xmax","ymin","ymax"])

class ScreenSpaceToRealSpaceMapper:
	'''
	Maps screenspace coordinates + depth to real (camera-centered) coordinates.
	
	Assumes coodinate system as below: 
	xy image coords / XYZ global coords
	     ^
	     | Y           Z = out of screen
	+----------------+
	|(0,0)      (x,0)|
	|                |  -> X
	|(0,y)      (x,y)|
	+----------------+
	Origin is at (0.5x,0.5y) at depth=0
	'''
	def __init__(self,*,image_width,image_height,reference_distance,reference_width):
		self._imgW=image_width
		self._imgH=image_height
		self._refdist=reference_distance
		self._refW=reference_width
		self._refH=reference_width/image_width*image_height
	def map_relcoords(self,*,relX,relY,depth):
		distance_factor=depth/self._refdist
		realX=(relX-0.5)*distance_factor*self._refW
		realY=(0.5-relY)*distance_factor*self._refH
		realZ=-depth
		return Point3D(x=realX,y=realY,z=realZ)
	def map_pxcoords(self,*,pxX,pxY,depth):
		return self.map_relcoords(
			relX=pxX/self._imgW,
			relY=pxY/self._imgH,
			depth=depth)
