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

def gaussian_blur(npa,sdev):
	return scipy.ndimage.gaussian_filter(
		npa,sdev,
		mode="nearest",truncate=3.0)
def box_blur(npa,siz):
	return scipy.ndimage.uniform_filter(
		npa,siz,
		mode="nearest")
