# Some math-related helper functions

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
