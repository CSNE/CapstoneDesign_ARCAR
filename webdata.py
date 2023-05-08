import web
import maths
import random

def depthmap_to_pointcloud_json(*,
	depth_map,color_image,
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
		csc=maths.screenspace_to_camspace((dmX,dmY),(dm_sizeX,dm_sizeY),d)
		#print(x,y,d,"-->",ssc)
		res.append( {
			"x":csc[0],
			"y":csc[1],
			"z":csc[2],
			"r":clr[0]/255,"g":clr[1]/255,"b":clr[2]/255})
	return res
