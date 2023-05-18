# Functions for combining YOLO and Depth data

import PIL.ImageFont
import numpy.ma
import numpy
import maths
import collections
import scipy.ndimage


import coordinates
from tuples import Tuples



'''
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
	["segment","name","point_list","confidence"]
	)
'''
Segment3D =collections.namedtuple(
	"Segment3D",
	["segment","name","confidence",
	 "point_list","point_list_flat","center_of_mass",
	 "depth_average","depth_min","depth_max",
	 "depth_valid","depth_valid_ratio",
	 "bbox","bbox_flat"])

def sample_matrix(*,relX,relY,mat):
	assert 0.0<=relX<=1.0
	assert 0.0<=relY<=1.0
	sizY,sizX=mat.shape
	x=round(relX*sizX-0.5)
	if x==sizX: x=sizX-1
	y=round(relY*sizY-0.5)
	if y==sizY: y=sizY-1
	return mat[y][x]


def segments_depth_combine(*,
		segments,
		sstrsm: coordinates.ScreenSpaceToRealSpaceMapper,
		depthmap,
		normal_sample_offset=None):
	'''
	Convert list of SegmentationResult into list of Segment3D
	'''
	
	dbg_img=PIL.Image.new("RGB",(depthmap.shape[1],depthmap.shape[0]))
	
	res=[]
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
		
		depth_average=intersection_masked_depth.mean()
		depth_min=intersection_masked_depth.min()
		depth_max=intersection_masked_depth.max()
		
		com=scipy.ndimage.center_of_mass(s.area)
		
		pl=[]
		plf=[]
		for i in range(len(s.points_ratio)):
			p=s.points_ratio[i]
			
			if normal_sample_offset:
				pointO=(p.x,p.y)
				
				if i==0:
					pointP=s.points_ratio[len(s.points_ratio)-1]
				else:
					pointP=s.points_ratio[i-1]
				if i==(len(s.points_ratio)-1):
					pointN=s.points_ratio[0]
				else:
					pointN=s.points_ratio[i+1]
				
				pointP=(pointP.x,pointP.y)
				pointN=(pointN.x,pointN.y)
				#print(F"+{pointP}")
				#print(F"-{pointN}")
				tangent = Tuples.normalize(Tuples.sub(pointN,pointP))
				#print(F"T{tangent}")
				normal = Tuples.rotate(tangent,deg=-90)
				#print(F"N{normal}")
				offset = Tuples.mult(normal,normal_sample_offset/100) #offset of image
				#print(F"O{offset}")
				applied= Tuples.add(pointO,offset)
				#print(F"S{samplepoint}")
				constrained= Tuples.elementwise_func(lambda x:min(max(x,0),1), applied)
				#print(F"C{constrained}")
				
				sample_point=constrained
				
				pxOx=round(pointO[0]*(depthmap.shape[1]-1))
				pxOy=round(pointO[1]*(depthmap.shape[0]-1))
				pxCx=round(constrained[0]*(depthmap.shape[1]-1))
				pxCy=round(constrained[1]*(depthmap.shape[0]-1))
				
				#print(pxO)
				dbg_img.putpixel([pxOx,pxOy],(255,0,255))
				dbg_img.putpixel([pxCx,pxCy],(0,255,0))
			else:
				sample_point=(p.x,p.y)
			
			d=sample_matrix(
				relX=sample_point[0],relY=sample_point[1],mat=depthmap)
			if d is numpy.ma.masked:
				pass
			else:
				c3d=sstrsm.map_relcoords(
					relX=p.x,relY=p.y,
					depth=d)
				pl.append(c3d)
				c3df=sstrsm.map_relcoords(
					relX=p.x,relY=p.y,
					depth=depth_average)
				plf.append(c3df)


		res.append(
			Segment3D(
				segment=s,
				name=s.name,
				confidence=s.confidence,
				point_list=pl,
				point_list_flat=plf,
				depth_average=depth_average,
				depth_min=depth_min,
				depth_max=depth_max,
				depth_valid=(valid_depth_pixel_count>1),
				depth_valid_ratio=depth_valid_ratio,
				center_of_mass=coordinates.Coordinates2D(x=com[1],y=com[0]),
				bbox=coordinates.calculateBbox3D(pl),
				bbox_flat=coordinates.calculateBbox3D(plf)))
	#dbg_img.save("out/seg3d_samplepoints.png")
	return res

def segments_3dify2(*,
		segments,
		sstrsm: coordinates.ScreenSpaceToRealSpaceMapper,
		depthmap,
		normal_sample_offset=None):
	# This is very dirty because i'm tired
	# i'll fix it later (ehh or probably not)
	
	sd2d=calculate_segdepth(segments,depthmap)
	s3d=segments_3dify(
		segments=segments,
		sstrsm=sstrsm,
		depthmap=depthmap,
		normal_sample_offset=normal_sample_offset)
	
	assert len(sd2d)==len(s3d)
	# Relies on the fact that two functions keep the ordering
	
	res=[]
	for i in range(len(sd2d)):
		res.append(
			Segment3D2(
				segment=sd2d[i].segment,
				name=s3d[i].name,
				point_list=s3d[i].point_list,
				confidence=s3d[i].confidence,
				depth_average=sd2d[i].depth_average))
	
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
