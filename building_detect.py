
import visualizations
import PIL.Image
import maths
import numpy
import numpy.ma
import cv2
import coordinates
import random
import collections
from tuples import Tuples
import scipy.ndimage

def derivative(dm):
	pass

def cluster(deriv_map):
	pass

# https://stackoverflow.com/a/66384452
def save_ma(fn,ma):
	numpy.savez_compressed(fn, data=ma.data, mask=ma.mask)
def load_ma(fn):
	with numpy.load(fn) as npz:
		arr = numpy.ma.MaskedArray(**npz)
	return arr
	
def _test_calc_save_depthmap():
	print("IGEV")
	import IGEV_Stereo.igev
	igev=IGEV_Stereo.igev.IGEVDriver(
		"IGEV_Stereo/pretrained_sceneflow.pth",
		use_cuda=False)
	
	print("Open/Resize")
	iL=PIL.Image.open("captures/building_L.jpg")
	iR=PIL.Image.open("captures/building_R.jpg")
	#iR=PIL.Image.open("captures/roadwalk12_fullstops/00547_00112092_R.jpg")
	
	iLs=maths.resize_fit(iL,(480,320))
	iRs=maths.resize_fit(iR,(480,320))
	
	print("Calculate")
	depth_igev = igev.calculate(
		left=iLs,
		right=iRs,
		depth_multiplier=50)
	
	print("Visualize")
	vis=visualizations.visualize_matrix(depth_igev,clip_percentiles=(5,85))
	vis.save("out/depthmap.png")
	
	print("Save")
	save_ma("test_depthmap.npz",depth_igev)

PlaneDefinition=collections.namedtuple(
	"PlaneDefinition",
	["originX","originY","originZ","gradientX","gradientY","f"])

def linear_approximate(depthmap,sample_point:coordinates.Coordinates2D,sample_radius):
	xp=coordinates.Coordinates2D(x=sample_point.x+sample_radius,y=sample_point.y)
	xm=coordinates.Coordinates2D(x=sample_point.x-sample_radius,y=sample_point.y)
	yp=coordinates.Coordinates2D(x=sample_point.x,y=sample_point.y+sample_radius)
	ym=coordinates.Coordinates2D(x=sample_point.x,y=sample_point.y-sample_radius)
	
	gradX= (depthmap[xp.y][xp.x] - depthmap[xm.y][xm.x])/(sample_radius*2)
	gradY= (depthmap[yp.y][yp.x] - depthmap[ym.y][ym.x])/(sample_radius*2)
	center=depthmap[sample_point.y][sample_point.x]
	

	#print(F"gX{gradX} gY{gradY} nX{normal_vec[0]} nY{normal_vec[1]}")
	
	def plane(y,x):
		dx=x-sample_point.x
		dy=y-sample_point.y
		return center + gradX*dx + gradY*dy
		
	return PlaneDefinition(
		originX=sample_point.x,
		originY=sample_point.y,
		originZ=center,
		gradientX=gradX,
		gradientY=gradY,
		f=plane)

def realize_plane(shape,pd:PlaneDefinition):
	return numpy.fromfunction(pd.f,shape)
	

PlaneMatchResult=collections.namedtuple(
	"PlaneMatchResult",
	["match_ratio","plane_definition","normal_vector","mask","error","depth","center_real","center_map"])
def get_fit_candidates(depthmap,n,r,sstrsm):
	res=[]
	for i in range(n):
		testpoint=coordinates.Coordinates2D(
			x=random.randint(r,depthmap.shape[1]-r-1),
			y=random.randint(r,depthmap.shape[0]-r-1))
		
		pd=linear_approximate(depthmap,testpoint,r)
		depth=pd.originZ
		
		px_to_meters=sstrsm.map_pxdistance(distX=1,distY=1,depth=depth)
		nvec=Tuples.normalize([pd.gradientX/px_to_meters.x,-pd.gradientY/px_to_meters.y,1])
		plane=realize_plane(depthmap.shape,pd)
		#visualizations.visualize_matrix(plane).save("out/plane.png")
		error=depthmap-plane
		#visualizations.visualize_matrix(ext_error,clip_values=(-1,+2)).save("out/err.png")
		
		err_threshd=numpy.ma.masked_greater(numpy.absolute(error),depth*0.05) #MAGIC: depth thressh
		ratio=err_threshd.count() / err_threshd.size
		
		mask=numpy.logical_not(err_threshd.mask)
		#print(err_threshd.dtype)
		com=scipy.ndimage.center_of_mass(mask)
		comZ=pd.f(*com)
		com_real=sstrsm.map_pxcoords(pxX=com[1],pxY=com[0],depth=comZ)
		#print("COM",com)
		#print("COMr",com_real)
		
		
		
		#print((pd,ratio))
		res.append(PlaneMatchResult(
			match_ratio=ratio,
			plane_definition=pd,
			normal_vector=nvec,
			mask=mask,
			error=error,
			depth=depth,
			center_real=com_real,
			center_map=coordinates.Coordinates2D(x=com[1],y=com[0])))
	
	res=[i for i in res if i.depth<30] #MAGIC: maximum distance
	res.sort(key=lambda x:x.match_ratio, reverse=True) # High matches first
	
	for i in res:
		pass
		#print(i)
	
	# Remove duplicates
	i=0
	while i<len(res):
		j=len(res)-1
		while j>i:
			nv_delta=Tuples.mag(
				Tuples.sub(
					res[i].normal_vector,
					res[j].normal_vector))
			#print("NV-i",res[i][1].normal_vector)
			#print("NV-j",res[j][1].normal_vector)
			#print("NV Delta",nv_delta)
			if nv_delta<0.5: #MAGIC: normal duplicate threshold
				#print("Remove",j)
				del res[j]
			j-=1
		i+=1
		
	for i in res:
		pass
		#print(i)
	
	
		
	return res[:10]
			
		
def _test_infer_gradient():
	depth=load_ma("test_depthmap.npz")
	ss2rsm=coordinates.ScreenSpaceToRealSpaceMapper(
		image_width=depth.shape[1],image_height=depth.shape[0],
		reference_distance=5,reference_width=8)
	
	visualizations.visualize_matrix(depth,clip_percentiles=(5,85)).save("out/loaded_DM.png")
	
	depth_blurred=maths.gaussian_blur(depth,5)
	visualizations.visualize_matrix(depth_blurred,clip_percentiles=(5,85)).save("out/dm_blurred.png")
	
	fc=get_fit_candidates(depth_blurred,100,10,ss2rsm)
	for i in range(len(fc)):
		print(i)
		print("  ",fc[i].match_ratio)
		print("  ",fc[i].plane_definition)
		print("  ",fc[i].normal_vector)
		print("  ",fc[i].center_real)
		visualizations.visualize_matrix(
			fc[i].mask,
			annotate_point=fc[i].center_map).save(F"out/fit{i}.png")
		visualizations.visualize_matrix(
				depth_blurred-realize_plane(
					depth_blurred.shape,
					fc[i].plane_definition),
			clip_values=(-2,+2),
			cmap="seismic",
			annotate_point=coordinates.Coordinates2D(
						x=fc[i].plane_definition.originX,
						y=fc[i].plane_definition.originY)).save(F"out/err{i}.png")
	
	
def _test_infer_pc_ransac():
	pass
	
if __name__=="__main__":
	#_test_calc_save_depthmap()
	_test_infer_gradient()
	
