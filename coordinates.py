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
BBox3D = collections.namedtuple(
	"BBox3D",
	["xmin","xmax","ymin","ymax","zmin","zmax"])

def calculateBbox3D(pointlist:Point3D) -> BBox3D:
	x=[]
	y=[]
	z=[]
	for p in pointlist:
		x.append(p.x)
		y.append(p.y)
		z.append(p.z)
	return BBox3D(
		xmin=min(x),
		xmax=max(x),
		ymin=min(y),
		ymax=max(y),
		zmin=min(z),
		zmax=max(z))

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
	def map_reldistance(self,*,distX,distY,depth):
		distance_factor=depth/self._refdist
		realX=distX*distance_factor*self._refW
		realY=distY*distance_factor*self._refH
		return Coordinates2D(x=realX,y=realY)
	def map_pxdistance(self,*,distX,distY,depth):
		return self.map_reldistance(
			distX=distX/self._imgW,
			distY=distY/self._imgH,
			depth=depth)
	def relcoords_to_pxcoords(self,*,relX,relY):
		return Coordinates2D(x=relX*self._imgW,y=relY*self._imgH)
