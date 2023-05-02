import kinect_common
import datetime
import os.path
import os
import time


import PIL.Image
import numpy


def pil_to_npa(pimg):
	return numpy.array(pimg)
def npa_to_pil(npa):
	return PIL.Image.fromarray(npa)

def save_capture(filepath:str, kcd:kinect_common.KinectCaptureData):
	numpy.savez(
		filepath,
		colorimage=pil_to_npa(kcd.color_image),
		depth_raw=kcd.depth_data_raw,
		depth_mapped=kcd.depth_data_mapped)
def load_capture(filepath:str) -> kinect_common.KinectCaptureData:
	with numpy.load(filepath) as dat:
		return kinect_common.KinectCaptureData(
			color_image=npa_to_pil(dat["colorimage"]),
			depth_data_raw=dat["depth_raw"],
			depth_data_mapped=kinect_common.filter_out_zeros(dat["depth_mapped"]))

def capture_video(
	*,
	res:str,
	ir:str,
	fps:str,
	period:float,
	comment:str):

	import tk_display
	import kinect_hardware

	param_str=F"R[{res}]_I[{ir}]_F[{fps}]_P[{period}]"

	img_disp_root=tk_display.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition
	idw=tk_display.ImageDisplayWindow(img_disp_root,"Preview")



	timestr=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	dirname=timestr+"_"+comment+"_"+param_str

	savedir=os.path.join("kinect_captures",dirname)
	print(savedir)
	os.mkdir(savedir)

	k4a = kinect_hardware.getK4A(res,ir,fps)
	k4a.start()

	frameN=0
	startT=time.time()
	lastSuccessfulLoopBeginT=startT
	while True:
		# Keep constant loop rate
		while time.time()<lastSuccessfulLoopBeginT+period:
			time.sleep(0.01)
		loopBeginT=time.time()

		kcd = kinect_hardware.getCap(k4a)
		if detect_error(kcd.color_image):
			print("Errored! Retry....")
			time.sleep(0.1)
			continue

		lastSuccessfulLoopBeginT=loopBeginT
		idw.set_image(kcd.color_image)

		frameNstr="F{:05d}".format(frameN)
		frameT=time.time()-startT
		frameTstr="{:06d}ms".format(round(frameT*1000))
		print("Save frame",frameNstr,frameTstr)

		savepath=os.path.join(savedir,F"{frameNstr}_{frameTstr}.npz")
		save_capture(savepath,kcd)

		frameN+=1

def playback(path):
	if os.path.exists(path):
		if os.path.isdir(path):
			files=os.listdir(path)
			files.sort()

def detect_error(pimg):
	# Return True if image seems errored

	npa=numpy.array(pimg)
	npa=npa.transpose([2,0,1]) # C Y X
	ry=max_rowdiff(npa[0])
	gy=max_rowdiff(npa[1])
	by=max_rowdiff(npa[2])
	npa=npa.transpose([0,2,1]) # C X Y
	rx=max_rowdiff(npa[0])
	gx=max_rowdiff(npa[1])
	bx=max_rowdiff(npa[2])
	print(F"ry{ry:.1f} gy{gy:.1f} by{by:.1f} rx{rx:.1f} gx{gx:.1f} bx{bx:.1f}")

	return max(ry,gy,by,rx,gx,bx)>20

def max_rowdiff(npa):
	#print("RowDiff on",npa.shape)
	prev_mean=None
	maxdiff=0
	for row in npa:
		mean=row.mean()
		if prev_mean is not None:
			diff=mean-prev_mean
			maxdiff=max(diff,maxdiff)
		prev_mean=mean
	return maxdiff

if __name__=="__main__":
	capture_video(
		comment="walk",
		res="720",
		ir="nu",
		fps="30",
		period=0.2)