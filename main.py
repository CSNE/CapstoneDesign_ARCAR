
# Arguments parse
import arguments


# Imports
# Standard Library
import time
import os.path
import os
import random
import traceback


# 3rd party
import PIL.Image
import PIL.ImageGrab
import cv2
import numpy as np

# Local modules
if arguments.output=="tk":
	import tk_display
import yolodriver
import monodepth_driver
if arguments.source in ("webcam","webcam_stereo"):
	import webcam
if arguments.source=="video":
	import video
if arguments.output=="web":
	import web
	import webdata
import maths
import combined
if arguments.source=="kinect":
	import kinect_hardware
import visualizations
if arguments.source=="kinectcapture":
	import kinect_record
import stereo
if arguments.stereo_solver=="psm":
	import PSMNet.psm

# Make YOLO quiet
import ultralytics.yolo.utils
import logging
ultralytics.yolo.utils.LOGGER.setLevel(logging.WARNING)
if arguments.verblevel>2:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.INFO)
if arguments.verblevel>3:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.DEBUG)




# Simple timer
class SequenceTimer:
	def __init__(self):
		self._current_segment_name=None
		self._current_segment_start=None
	def _start_segment(self,name,t):
		self._current_segment_name=name
		self._current_segment_start=t
	def _end_segment(self,t):
		if self._current_segment_name is None:
			return
		n=self._current_segment_name
		delta=t-self._current_segment_start
		print("{:>16s}: {:>6.1f}ms".format(n,delta*1000))
		self._current_segment_name=None
		self._current_segment_start=None
	def start(self,name):
		t=time.time()
		self._end_segment(t)
		self._start_segment(name,t)
	def end(self):
		self._end_segment(time.time())


# Global variables
timer=SequenceTimer()
cleanup_functions=[]


## GUI Setup
if arguments.output=="tk":
	img_disp_root=tk_display.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	tid_hud_seg=tk_display.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_camraw=tk_display.ImageDisplayWindow(img_disp_root,"Source Image")
	#tid_depth=tk_display.ImageDisplayWindow(img_disp_root,"Depth Estimation")
	tid_combined=tk_display.ImageDisplayWindow(img_disp_root,"Combined")
	tid_depthAI=tk_display.ImageDisplayWindow(img_disp_root,"AI Depth")
	tid_depthIR=tk_display.ImageDisplayWindow(img_disp_root,"IR Depth")
	tid_depthCompare=tk_display.ImageDisplayWindow(img_disp_root,"Depth Compare")

# Web Server setup
if arguments.output=="web":
	server_port=28301
	st=web.ServerThread(server_port)
	st.start()
	cleanup_functions.append(lambda:st.die())
	with open("webpage.html","rb") as f:
		page=f.read()
	st.put_data("/",page)
	with open("webpage.js","rb") as f:
		page=f.read()
	st.put_data("/webpage.js",page,"text/javascript")
	time.sleep(1.0)


# Display function
frmN=0
def display(img,*,alt_img=None,ir_depth=None):
	global frmN
	frmN+=1
	print(F"\nFrame {frmN}")
	
	if arguments.output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	

	timer.start("Segmentation")
	# Segmentation
	segs=yolodriver.segment(img)
	seg_vis=visualizations.visualize_segmentations(segs,img.size)
	

	timer.start("Depth")
	# Depth estimation
	ai_depth=monodepth_driver.estimate_depth(img,depth_multiplier=0.3)

	if ir_depth is not None:
		compare_vis=visualizations.compare_depthmaps(
			ai=ai_depth,ir=ir_depth)
		#compared.show()
		ir_vis=visualizations.visualize_matrix(ir_depth,"IR Depth",clip_percentiles=(5,95))
		if hasattr(ir_depth,"count"): # Only has it if MaskedArray
			print("IR avail: {}/{}".format(ir_depth.count(),ir_depth.size))
	else:
		compare_vis=PIL.Image.new("RGB",(16,16))
		ir_vis=PIL.Image.new("RGB",(16,16))
	ai_vis=visualizations.visualize_matrix(ai_depth,"AI Depth")

	if ir_depth is None:
		depth=ai_depth
	else:
		depth=ir_depth

	dvis=visualizations.visualize_matrix(depth)
	

	timer.start("Combining")
	# Combine
	segdepths_raw=combined.calculate_segdepth(segs,depth)

	# Filter out SegDepths with too little depth data
	segdepths_valid=[]
	for sd in segdepths_raw:
		if sd.depth_valid_ratio<0.1:
			continue
		segdepths_valid.append(sd)
	diff=len(segdepths_raw)-len(segdepths_valid)
	if diff != 0:
		print(F"Removed {diff} SegDepths out of {len(segdepths_raw)} because of insufficient depth data")

	# Visualize Segdepths
	combined_vis=visualizations.visualize_segdepth(segdepths_valid,img.size,img)
	

	timer.start("Output")
	# Output
	if arguments.output=="tk":
		tid_camraw.set_image(img)
		tid_hud_seg.set_image(seg_vis)
		#tid_depth.set_image(dvis)
		tid_combined.set_image(combined_vis)
		tid_depthAI.set_image(ai_vis)
		tid_depthIR.set_image(ir_vis)
		tid_depthCompare.set_image(compare_vis)
	elif arguments.output=="web":
		st.put_image("/raw.jpg",img)
		st.put_image("/seg.jpg",seg_vis)
		if alt_img is not None:
			st.put_image("/str.jpg",alt_img)
			st.put_image("/dif.jpg",PIL.ImageChops.difference(img,alt_img))
		st.put_image("/com.jpg",combined_vis)
		st.put_string("/information",str(frmN))
		objects_json=combined.segdepths_to_json(segdepths_valid,img)
		st.put_json("/objects",objects_json)
		pointcloud_json=webdata.depthmap_to_pointcloud_json(
			depth_map=ai_depth,
			color_image=img,
			sampleN=3000)
		st.put_json("/pointcloud.json",pointcloud_json)
		st.put_image("/dai.jpg",ai_vis)
		st.put_image("/dir.jpg",ir_vis)
		st.put_image("/dcm.jpg",compare_vis)
	elif arguments.output=="file":
		img.save("out/raw.jpg")
		seg_vis.save("out/seg.jpg")
		if alt_img is not None:
			alt_img.save("out/alt.jpg")
			PIL.ImageChops.difference(img,alt_img).save("out/dif.jpg")
		combined_vis.save("out/combined.jpg")
		compare_vis.save("out/compare.jpg")
		ir_vis.save("out/depthIR.jpg")
		ai_vis.save("out/depthAI.jpg")
	timer.start("Get Frame")

def stereo_solve(pimL,pimR):
	if arguments.stereo_solver=="opencv":
		return stereo.stereo_calculate(
			left=pimL,right=pimR,
			depth_multiplier=1000) #MAGIC: Depth correction factor
	elif arguments.stereo_solver=="psm":
		pimL=maths.resize_fit(pimL,(480,320))
		pimR=maths.resize_fit(pimR,(480,320))
		return PSMNet.psm.calculate(pimL,pimR)*(0.1) #MAGIC: Depth correction factor
	else:
		0/0
		
# Main capture loop
def capture_loop():
	if arguments.source=="webcam":
		camera=webcam.Webcam(arguments.wc)
		while True:
			pim=camera.grab()
			display(pim)
			if arguments.singleframe: break
	if arguments.source=="webcam_stereo":
		cameraL=webcam.ThreadedWebcam(arguments.wcL)
		cameraR=webcam.ThreadedWebcam(arguments.wcR)
		cameraL.start()
		cameraR.start()
		cleanup_functions.append(lambda:cameraL.die())
		cleanup_functions.append(lambda:cameraR.die())
		time.sleep(0.5)
		while True:
			pimL=cameraL.grab()
			pimR=cameraR.grab()
			#print("R",pimR)
			#print("L",pimL)
			if (pimL is None) or (pimR is None):
				print("Webcam image is null. Retry...")
				time.sleep(0.1)
				continue
			disparity=stereo_solve(pimL,pimR)
			display(pimL,alt_img=pimR,ir_depth=disparity)
			if arguments.singleframe: break
	elif arguments.source=="kinect":
		k4a=kinect_hardware.getK4A(
			arguments.kinect_rgb,
			arguments.kinect_depth,
			arguments.kinect_fps)
		k4a.start()
		while True:
			kcd=kinect_hardware.getCap(k4a)
			display(kcd.color_image,ir_depth=kcd.depth_data_mapped)
			if arguments.singleframe: break
	elif arguments.source=="image":
		while True:
			display(PIL.Image.open(arguments.infile))
			if arguments.singleframe: break
	elif arguments.source=="image_stereo":
		while True:
			iL=PIL.Image.open(arguments.infileL).convert("RGB")
			iR=PIL.Image.open(arguments.infileR).convert("RGB")
			disparity=stereo_solve(iL,iR)
			display(iL,alt_img=iR,ir_depth=disparity)
			if arguments.singleframe: break
	elif arguments.source=="video":
		startT=time.time()
		while True:
			vt=(time.time()-startT)*arguments.vs
			vf=video.get_video_frame(arguments.infile,vt)
			display(vf)
			if arguments.singleframe: break

	elif arguments.source=="screenshot":
		while True:
			display(PIL.ImageGrab.grab(arguments.sr))
			if arguments.singleframe: break

	elif arguments.source=="kinectcapture":
		if os.path.isdir(arguments.infile):
			filepaths=[
				os.path.join(arguments.infile,fn)
				for fn in os.listdir(arguments.infile)]
		else:
			filepaths=[arguments.infile]
		filepaths.sort()
		
		playback_autonext=False
		playback_frameN=0
		playback_lastN=None

		if arguments.output=="web":
			def playback_countrol_handler(q):
				nonlocal playback_autonext
				nonlocal playback_frameN
				t=q["type"][0]
				print("PCH",t)
				if t=="pause":
					playback_autonext=False
				elif t=="play":
					playback_autonext=True
				elif t=="+1":
					playback_frameN+=1
				elif t=="-1":
					playback_frameN-=1
				elif t=="-10":
					playback_frameN-=10
				elif t=="+10":
					playback_frameN+=10
				elif t=="-100":
					playback_frameN-=100
				elif t=="+100":
					playback_frameN+=100
				elif t=="rand":
					playback_frameN=random.randint(0,len(filepaths)-1)
				else:
					print("Unknown command",q)
			st.set_handler("/playbackControl",playback_countrol_handler)

		while True:
			if playback_autonext:
				playback_frameN+=1

			if playback_frameN != playback_lastN:
				while True:
					if playback_frameN<0:
						playback_frameN=0
					playback_frameN=playback_frameN%len(filepaths)
					print("Load",playback_frameN)
					kcd=kinect_record.load_capture(filepaths[playback_frameN])
					err=kinect_record.detect_error(kcd.color_image)
					if err:
						print("Image seems errored. Get another frame.")
						playback_frameN+=1
						continue
					display(kcd.color_image,ir_depth=kcd.depth_data_mapped)
					playback_lastN=playback_frameN
					break
			else:
				time.sleep(0.1)
			if arguments.singleframe: break
			#input()



try:
	capture_loop()
	input("Press Enter to exit.")
except KeyboardInterrupt:
	print("^C Received. Exiting...")
except:
	traceback.print_exc()
finally:
	print("Cleanup...")
	for i in cleanup_functions:
		i()
print("Main thread terminated.")
