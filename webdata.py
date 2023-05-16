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

def segdepths_to_json(
		segdepths: typing.List[combined.SegDepth2D],
		orig_img: PIL.Image,
		mapper:coordinates.ScreenSpaceToRealSpaceMapper):
	'''
	Pack all the segdepth data into a JSON,
	to be used in the browser visualizer.
	'''
	orig_img_size=orig_img.size
	objects_json=[]
	for sd in segdepths:
		dep=sd.depth_average
		seg=sd.segment
		
		# Calculate bounding boxes
		bbox_center_X=(seg.bbox_pixel.xmin+seg.bbox_pixel.xmax)/2
		bbox_size_X=seg.bbox_pixel.xmax-seg.bbox_pixel.xmin
		bbox_center_Y=(seg.bbox_pixel.ymin+seg.bbox_pixel.ymax)/2
		bbox_size_Y=seg.bbox_pixel.ymax-seg.bbox_pixel.ymin
		
		
		acXmin, acYmin, _ = mapper.map_pxcoords(
			pxX=seg.bbox_pixel.xmin,
			pxY=seg.bbox_pixel.ymax,
			depth=dep)
		acXmax, acYmax, _ = mapper.map_pxcoords(
			pxX=seg.bbox_pixel.xmax,
			pxY=seg.bbox_pixel.ymin,
			depth=dep)
		
		actual_coords_X=(acXmax+acXmin)/2
		actual_coords_Y=(acYmax+acYmin)/2
		actual_size_X=(acXmax-acXmin)
		actual_size_Y=(acYmax-acYmin)
		
		# Get texture, a 100x100(max) JPG in b64 format
		tex=orig_img.crop((
			seg.bbox_pixel.xmin,seg.bbox_pixel.ymin,
			seg.bbox_pixel.xmax,seg.bbox_pixel.ymax))
		if tex.width>tex.height:
			if tex.width>100:
				tex=tex.resize((100,round(100/tex.width*tex.height)))
		else:
			if tex.height>100:
				tex=tex.resize((round(100/tex.height*tex.width),100))
		
		bio=io.BytesIO()
		tex.save(bio,format="JPEG")
		b64=base64.b64encode(bio.getvalue()).decode()
		
		# Finally, pack it into a JSON-able format
		obj_data={"name":str(seg.name),
			 "coordX":float(actual_coords_X),
			 "coordY":float(actual_coords_Y),
			 "coordZ":float(dep),
			 "sizeX":float(actual_size_X),
			 "sizeY":float(actual_size_Y),
			 "texture":"data:image/jpeg;base64,"+b64}
		
		objects_json.append(obj_data)
	return objects_json

def seg3d_to_json(seg3ds:typing.List[combined.Segment3D]):
	obj=[]
	for seg3d in seg3ds:
		pointlist=[]
		for point in seg3d.point_list:
			pointlist.append([point.x,point.y,point.z])
		obj.append(
			{"name":seg3d.name,
			 "pointlist":pointlist})
	return obj

'''
Text3D = collections.namedtuple(
	"Text3D",
	["text","size","x","y","z"])'''
centerMM = lambda l: (min(l)+max(l))/2 #Min-Max Center
median = lambda l: sorted(l)[len(l)/2]
avg=lambda l: sum(l)/len(l)
def seg3d_to_text_json(seg3ds:typing.List[combined.Segment3D]):
	obj=[]
	for seg3d in seg3ds:
		coordsX=[]
		coordsY=[]
		coordsZ=[]
		for point in seg3d.point_list:
			coordsX.append(point.x)
			coordsY.append(point.y)
			coordsZ.append(point.z)
		obj.append({
			"text":seg3d.name,
			"size":0.2,
			"x":avg(coordsX),
			"y":avg(coordsY),
			"z":avg(coordsZ)})
	return obj

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
