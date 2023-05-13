# Functions for combining YOLO and Depth data

import PIL.ImageFont
import numpy.ma
import numpy
import maths
import collections

import coordinates


# A namedtuple for storing the depth along with the segment.
# The segment is assumed to be flat.
SegDepth2D=collections.namedtuple(
	"SegDepth3D",
	["segment",
	 "depth_average","depth_min","depth_max",
	 "depth_valid","depth_valid_ratio"])

# A namedtuple for storing data about a 3D segment.
# The segment is a list of 
Segment3D = collections.namedtuple(
	"Segment3D",
	["name","point_list","confidence"]
	)

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

		
		result.append(SegDepth2D(
			segment=s,
			depth_average=intersection_masked_depth.mean(),
			depth_min=intersection_masked_depth.min(),
			depth_max=intersection_masked_depth.max(),
			depth_valid=(valid_depth_pixel_count>1),
			depth_valid_ratio=depth_valid_ratio))
	return result


def sample_matrix(*,relX,relY,mat):
	assert 0.0<=relX<=1.0
	assert 0.0<=relY<=1.0
	sizY,sizX=mat.shape
	x=round(relX*sizX-0.5)
	if x==sizX: x=sizX-1
	y=round(relY*sizY-0.5)
	if y==sizY: y=sizY-1
	return mat[y][x]

def segments_3dify(*,
		segments,
		sstrsm: coordinates.ScreenSpaceToRealSpaceMapper,
		depthmap):
	'''
	Convert list of SegmentationResult into list of Segment3D
	'''
	res=[]
	for s in segments:
		pl=[]
		for p in s.points_ratio:
			d=sample_matrix(
				relX=p.x,relY=p.y,mat=depthmap)
			c3d=sstrsm.map_relcoords(
				relX=p.x,relY=p.y,
				depth=d)
			pl.append(c3d)
		res.append(
			Segment3D(
				name=s.name,
				confidence=s.confidence,
				point_list=pl))
	return res



if __name__=="__main__":
	print("Import YOLO")
	import yolodriver
	print("Import PIL")
	import PIL.Image
	import visualizations
	print("Import MD2")
	import monodepth_driver
	de=monodepth_driver.DepthEstimator()
	img=PIL.Image.open("test_images/2630Social_distancing_and_panic_buying_36.jpg")
	segs=yolodriver.segment(img)
	dep=de.estimate(img)
	vis=visualizations.visualize_matrix(dep)
	vis.save("out/temp.png")
	
	
	
	sstrsm=coordinates.ScreenSpaceToRealSpaceMapper(
		image_width=img.width,
		image_height=img.height,
		reference_distance=5,
		reference_width=10)
	seg3ds=segments_3dify(
		segments=segs,
		sstrsm=sstrsm,
		depthmap=dep)
	for seg3d in seg3ds:
		print("SEGMENT:")
		print("  Name",seg3d.name)
		print("  Conf",seg3d.confidence)
		print("  Points:")
		for p in seg3d.point_list:
			print("    ",p)
		0/0
