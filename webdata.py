import web
import maths
import random
import PIL.Image
import combined
import typing
import coordinates
import io
import base64
import collections
import building_detect
import building_definitions
from typing import List
import magic

def depthmap_to_pointcloud_json(*,
	depth_map,color_image,
	mapper: coordinates.ScreenSpaceToRealSpaceMapper,
	sampleN=1000,regular_sampling=False):
	res=[]
	samples=maths.sample_npa(depth_map,sampleN)
	if regular_sampling:
		pass #TODO implement
		
	dm_sizeX=depth_map.shape[1]
	dm_sizeY=depth_map.shape[0]
	for dmY,dmX in samples:
		relX=dmX/dm_sizeX
		relY=dmY/dm_sizeY
		d=depth_map[dmY][dmX]
		clrX=round(color_image.width*relX)
		clrY=round(color_image.height*relY)
		clr=color_image.getpixel((clrX,clrY))
		
		#Cam-space coordinates
		csc=mapper.map_relcoords(
			relX=relX,
			relY=relY,
			depth=d)
		#print(x,y,d,"-->",ssc)
		res.append( {
			"x":csc[0],
			"y":csc[1],
			"z":csc[2],
			"r":clr[0]/255,"g":clr[1]/255,"b":clr[2]/255})
	return res


def seg3d_to_json(
		seg3ds:typing.List[combined.Segment3D],
		use_flat=False):
	obj=[]
	for seg3d in seg3ds:
		pointlist=[]
		
		if use_flat: plist=seg3d.point_list_flat
		else: plist=seg3d.point_list
		
		dist=seg3d.bbox_flat.zmin
		
		for point in plist:
			pointlist.append([point.x,point.y,point.z])
		obj.append(
			{"name":seg3d.name,
			 "width":dist*0.005,
			 "pointlist":pointlist})
	return obj

'''
Text3D = collections.namedtuple(
	"Text3D",
	["text","size","x","y","z"])'''
centerMM = lambda l: (min(l)+max(l))/2 #Min-Max Center
median = lambda l: sorted(l)[len(l)/2]
avg=lambda l: sum(l)/len(l)
def seg3d_to_text_json(
		seg3ds:typing.List[combined.Segment3D],
		use_flat=False):
	obj=[]
	for seg3d in seg3ds:

		x=(seg3d.bbox_flat.xmin+seg3d.bbox_flat.xmax)/2
		if magic.visuals.text3d_segment_centerY:
			y=(seg3d.bbox_flat.ymin+seg3d.bbox_flat.ymax)/2
		else:
			y=seg3d.bbox_flat.ymax
		z=seg3d.bbox_flat.zmin
		sz=magic.visuals.text3d_segment_size*abs(z)

		obj.append({
			"text":seg3d.name,
			"size":sz,
			"x":x,
			"y":y+sz/2,
			"z":z,
			"r":0.0,
			"g":1.0,
			"b":1.0})
	return obj
	
def seg3d_building_to_text_json(seg3d:combined.Segment3D,name):
	
	x=(seg3d.bbox_flat.xmin+seg3d.bbox_flat.xmax)/2
	y=(seg3d.bbox_flat.ymin+seg3d.bbox_flat.ymax)/2
	z=seg3d.bbox_flat.zmin
	sz=magic.visuals.text3d_building_size*abs(z)
		
	return {
		"text":name,
		"size":sz,
		"x":x,
		"y":y+sz/2,
		"z":z,
		"r":1.0,
		"g":1.0,
		"b":0.0}
	
def wall_to_json(pmrs:typing.List[building_detect.PlaneMatchResult]):
	obj=[]
	for pmr in pmrs:
		obj.append({
			"nvX":pmr.normal_vector[0],
			"nvY":pmr.normal_vector[1],
			"nvZ":pmr.normal_vector[2],
			"x":pmr.center_real.x,
			"y":pmr.center_real.y,
			"z":pmr.center_real.z})
	return obj


def gpsinfo_json(*,
	position,velocity_direction, looking_direction,
	buildings:List[building_definitions.BuildingLGC]):
	obj={}
	obj["velocity"] = velocity_direction
	obj["looking"] = looking_direction
	obj["position"] = position
	
	building_list=[]
	for b in buildings:
		building_list.append({
			"relX":b.lgc.x-position[0],
			"relY":b.lgc.y-position[1],
			"name":b.name})
	obj["buildings"] = building_list
	return obj
