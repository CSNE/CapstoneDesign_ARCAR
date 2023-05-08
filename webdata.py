import web
import maths

def depthmap_to_pointcloud_json(dm,sample=1000,regular_sampling=False):
	res=[]
	samples=maths.sample_npa(dm,sample)
	if regular_sampling:
		pass #TODO implement
	for y,x in samples:
		d=dm[y][x]
		ssc=maths.screenspace_to_camspace((x,y),(dm.shape[1],dm.shape[0]),d)
		#print(x,y,d,"-->",ssc)
		res.append( {
			"x":ssc[0],
			"y":ssc[1],
			"z":ssc[2],
			"r":1.0,"g":1.0,"b":1.0})
	return res
