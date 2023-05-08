# Functions for combining YOLO and Depth data

import base64
import io
import PIL.ImageFont
import numpy.ma
import numpy
import maths
import collections


# A namedtuple for storing the depth along with the segment.
SegDepth=collections.namedtuple(
	"SegDepth",
	["segment",
	 "depth_average","depth_min","depth_max",
	 "depth_valid","depth_valid_ratio"])

def calculate_segdepth(segments,depthmap):
	'''
	Calculate each segment's distance, by averaging the segment area
	in the depth map.
	Returns a list of SegDepths
	'''
	result=[]
	#depthmap_resized=None
	for s in segments:
		# YOLO provides the area as a float array of either 1.0 or 0.0
		# We resize this to fit the depth map size
		# And then convert it to MaskedArray
		area_resized=maths.resize_matrix(s.area,depthmap.shape)
		area_resized_masked=numpy.ma.masked_less_equal(area_resized, 0.5)
		
		# Combine masks.
		# Only take depth data if in segment area AND is valid depth
		# Mask is used for exclusion, not inclusion so we actually OR here.
		assert area_resized_masked.shape == depthmap.shape
		if hasattr(depthmap,"mask"): # Only if depthmap is maskedarray
			combined_mask=numpy.logical_or(area_resized_masked.mask,depthmap.mask)
		else:
			combined_mask=area_resized_masked.mask

		# Create maskedarray, take mean
		intersection_masked_depth=numpy.ma.MaskedArray(depthmap,mask=combined_mask)

		valid_depth_pixel_count=intersection_masked_depth.count()
		area_pixel_count=area_resized_masked.count()
		#print(area_pixel_count,valid_depth_pixel_count)
		depth_valid_ratio=valid_depth_pixel_count/area_pixel_count

		# No valid depth data

		
		result.append(SegDepth(
			segment=s,
			depth_average=intersection_masked_depth.mean(),
			depth_min=intersection_masked_depth.min(),
			depth_max=intersection_masked_depth.max(),
			depth_valid=(valid_depth_pixel_count>1),
			depth_valid_ratio=depth_valid_ratio))
	return result


	

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
		
		
		acXmin, acYmin, _ = maths.screenspace_to_camspace(
			(seg.xmin,seg.ymin),
			orig_img_size,
			dep)
		acXmax, acYmax, _ = maths.screenspace_to_camspace(
			(seg.xmax,seg.ymax),
			orig_img_size,
			dep)
		
		actual_coords_X=(acXmax+acXmin)/2
		actual_coords_Y=(acYmax+acYmin)/2
		actual_size_X=(acXmax-acXmin)
		actual_size_Y=(acYmax-acYmin)
		
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
