import torch.nn.functional
import numpy
import scipy.ndimage

def resize_matrix(mat,target_size):
	orig_size=mat.shape
	y_scale=target_size[0]/orig_size[0]
	x_scale=target_size[1]/orig_size[1]
	return scipy.ndimage.zoom(mat.astype(float),(y_scale,x_scale))

if __name__=="__main__":
	nda=numpy.array([[1,2,3],[4,5,6],[7,8,9]])
	print(nda,nda.shape,type(nda),nda.dtype)
	rsz=resize_matrix(nda,(5,5))
	print(rsz,rsz.shape,type(rsz),rsz.dtype)
