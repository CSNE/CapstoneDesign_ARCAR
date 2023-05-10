# Some math-related helper functions

import random

import numpy
import scipy.ndimage

def resize_matrix(mat,target_size):
	'''
	Resize matrix mat to target size.
	Interpolates the values, like how you would scale an image.
	Used for resizing the depth map.
	'''
	orig_size=mat.shape
	y_scale=target_size[0]/orig_size[0]
	x_scale=target_size[1]/orig_size[1]
	return scipy.ndimage.zoom(mat.astype(float),(y_scale,x_scale))

def fit(box,bound):
	box=list(box)
	if box[0]>bound[0]:
		box[1]=box[1]*(bound[0]/box[0])
		box[0]=bound[0]
	if box[1]>bound[1]:
		box[0]=box[0]*(bound[1]/box[1])
		box[1]=bound[1]
	return (round(box[0]),round(box[1]))

def resize_fit(img,bound):
	target_size=fit(img.size,bound)
	if target_size != img.size:
		img=img.resize(target_size)
	return img

if __name__=="__main__":
	# Testing code
	nda=numpy.array([[1,2,3],[4,5,6],[7,8,9]])
	print(nda,nda.shape,type(nda),nda.dtype)
	rsz=resize_matrix(nda,(5,5))
	print(rsz,rsz.shape,type(rsz),rsz.dtype)

def screenspace_to_camspace(cxy,sxy,d):
	# cxy - Screen coords, XY 
	# sxy - Image dimensions, XY
	# d - depth
	# Returns (X,Y,Z) real-space coords
	bbox_center_X=cxy[0]
	bbox_center_Y=cxy[1]
	orig_img_size=sxy
	
	# TODO actually formalize this crude conversion process
	#      maybe use matrices or something
	# Map screen-space coordinates to real-world relative coordinates
	# this is a very crude conversion - should probably refine later.
	# 5 meters is the reference point - calibrate later
	distance_scaling_factor=d/5 #MAGIC
	# at reference distance, how large is the screen? - again, calibrate later
	screen_dim_X=8 #MAGIC
	screen_dim_Y=screen_dim_X/orig_img_size[0]*orig_img_size[1]
	rel_coords_X=(bbox_center_X-(orig_img_size[0]/2))/orig_img_size[0]
	actual_coords_X=rel_coords_X*screen_dim_X*distance_scaling_factor
	#actual_size_X=bbox_size_X/orig_img_size[0]*screen_dim_X*distance_scaling_factor
	rel_coords_Y=(bbox_center_Y-(orig_img_size[1]/2))/orig_img_size[1]
	actual_coords_Y=rel_coords_Y*screen_dim_Y*distance_scaling_factor
	#actual_size_Y=bbox_size_Y/orig_img_size[1]*screen_dim_Y*distance_scaling_factor
	return float(actual_coords_X),float(actual_coords_Y),float(d)

def sample_npa(npa,sample=100):
	# Sample a 2D numpy array. May be masked.
	ir=npa
	if hasattr(ir,"mask"): #MaskedArray (Kinect)
		valid_ir_coords=numpy.transpose(numpy.nonzero(~ir.mask)).tolist()
		sampleN=min(sample,len(valid_ir_coords))
		sample_points=random.sample(valid_ir_coords,sampleN)
	else: #Regular array (CV2 Stereoscopy)
		sample_points=[
			(random.randint(0,ir.shape[0]-1),
			 random.randint(0,ir.shape[1]-1)) for i in range(sample)]
	return sample_points
