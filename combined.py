# Functions for combining YOLO and Depth data

import base64
import io
import PIL.ImageFont
import numpy.ma
import maths
import collections

# A namedtuple for storing the depth along with the segment.
SegDepth=collections.namedtuple(
	"SegDepth",["segment","depth_average","depth_min","depth_max"])

def calculate_segdepth(segments,depthmap):
	'''
	Calculate each segment's distance, by averaging the segment area
	in the depth map.
	Returns a list of SegDepths
	'''
	result=[]
	depthmap_resized=None
	for s in segments:
		# YOLO provides the area as a float array of either 1.0 or 0.0
		# We cast that to a boolean and invert it
		# Refer to the numpy.MaskedArray docs for why
		area_bool=~s.area.astype(bool)
		
		# Resize depth map to area map
		if depthmap_resized is None: # cache it
			depthmap_resized=maths.resize_matrix(depthmap,s.area.shape)
		# sanity check - the shape's dimensions should be consistent i think
		assert depthmap_resized.shape == s.area.shape
		
		# Masked array
		masked_depth=numpy.ma.MaskedArray(depthmap_resized,mask=area_bool)
		depth_mean=masked_depth.mean()
		
		result.append(SegDepth(
			segment=s,
			depth_average=masked_depth.mean(),
			depth_min=masked_depth.min(),
			depth_max=masked_depth.max()))
	return result

font=PIL.ImageFont.truetype("/usr/share/fonts/TTF/Hack-Bold.ttf",size=36)
def visualize_segdepth(segdepths,size):
	'''
	Visualize segdepths.
	'''
	vis=PIL.Image.new("RGB",size)
	draw=PIL.ImageDraw.Draw(vis)
	
	for sd in segdepths:
		
		dep=sd.depth_average
		seg=sd.segment
		
		bbox_center_X=(seg.xmin+seg.xmax)/2
		bbox_center_Y=(seg.ymin+seg.ymax)/2
		
		# Draw outline
		for i in range(len(seg.points)):
			j=i-1
			startX=seg.points[i][0]*size[0]
			startY=seg.points[i][1]*size[1]
			endX=  seg.points[j][0]*size[0]
			endY=  seg.points[j][1]*size[1]
			draw.line((startX,startY,endX,endY),fill="#FF0000",width=3)
			
		# Write text
		draw.text((bbox_center_X,bbox_center_Y),F"{seg.name}\n{dep:.1f}m",
			fill="#00FFFF",font=font,anchor="ms")
	return vis

def segdepths_to_json(segdepths,orig_img):
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
		bbox_center_X=(seg.xmin+seg.xmax)/2
		bbox_size_X=seg.xmax-seg.xmin
		bbox_center_Y=(seg.ymin+seg.ymax)/2
		bbox_size_Y=seg.ymax-seg.ymin
		
		# Map screen-space coordinates to real-world relative coordinates
		# this is a very crude conversion - should probably refine later.
		# 5 meters is the reference point - calibrate later
		distance_scaling_factor=dep/5
		# at reference distance, how large is the screen? - again, calibrate later
		screen_dim_X=7
		screen_dim_Y=screen_dim_X/orig_img_size[0]*orig_img_size[1]
		rel_coords_X=(bbox_center_X-(orig_img_size[0]/2))/orig_img_size[0]
		actual_coords_X=rel_coords_X*screen_dim_X*distance_scaling_factor
		actual_size_X=bbox_size_X/orig_img_size[0]*screen_dim_X*distance_scaling_factor
		rel_coords_Y=(bbox_center_Y-(orig_img_size[1]/2))/orig_img_size[1]
		actual_coords_Y=rel_coords_Y*screen_dim_Y*distance_scaling_factor
		actual_size_Y=bbox_size_Y/orig_img_size[1]*screen_dim_Y*distance_scaling_factor
		
		
		# Get texture, a 100x100(max) JPG in b64 format
		tex=orig_img.crop((seg.xmin,seg.ymin,seg.xmax,seg.ymax))
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
