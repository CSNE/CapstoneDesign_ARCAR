
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
import numpy.ma

# ANSI Console Colors
CC_RESET = '\033[0m'
CC_BOLD  = '\033[1m'
CC_BLINK = '\033[5m'
CC_FAINT = '\033[2m'

CC_BLACK   = '\033[30m'
CC_RED     = '\033[31m'
CC_GREEN   = '\033[32m'
CC_YELLOW  = '\033[33m'
CC_BLUE    = '\033[34m'
CC_MAGENTA = '\033[35m'
CC_CYAN    = '\033[36m'
CC_WHITE   = '\033[37m'

CC_BLACK_B   = '\033[90m'
CC_RED_B     = '\033[91m'
CC_GREEN_B   = '\033[92m'
CC_YELLOW_B  = '\033[93m'
CC_BLUE_B    = '\033[94m'
CC_MAGENTA_B = '\033[95m'
CC_CYAN_B    = '\033[96m'
CC_WHITE_B   = '\033[97m'

# Local modules
if arguments.output=="tk":
	import tk_display
import yolodriver

if arguments.source in ("webcam","webcam_stereo"):
	import webcam
if arguments.source=="video":
	import video
if arguments.output=="web":
	import web
	import webdata
import maths
import combined
import visualizations
if arguments.source=="kinectcapture":
	import kinect_record
if arguments.stereo_solvers["opencv"]:
	print(CC_YELLOW+"Using stereo solver: "+CC_BOLD+"OpenCV"+CC_RESET)
	import stereo
if arguments.stereo_solvers["monodepth"]:
	print(CC_YELLOW+"Using stereo solver: "+CC_BOLD+"MonoDepth2"+CC_RESET)
	import monodepth_driver
if arguments.stereo_solvers["psm"]:
	print(CC_YELLOW+"Using stereo solver: "+CC_BOLD+"PSMNet"+CC_RESET)
	import PSMNet.psm
if arguments.stereo_solvers["igev"]:
	print(CC_YELLOW+"Using stereo solver: "+CC_BOLD+"IGEV"+CC_RESET)
	import IGEV_Stereo.igev

# Make YOLO quiet
import ultralytics.yolo.utils
import logging
ultralytics.yolo.utils.LOGGER.setLevel(logging.WARNING)
if arguments.verblevel>2:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.INFO)
if arguments.verblevel>3:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.DEBUG)

if arguments.stereo_solvers["igev"]:
	# Setup IGEV
	igev=IGEV_Stereo.igev.IGEVDriver("IGEV_Stereo/pretrained_sceneflow.pth")



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
		print(CC_BLUE+CC_BOLD+F"{n:>24s}: "+CC_RESET,end='')
		if delta<0.2:
			clr=CC_GREEN
		elif delta<1.0:
			clr=CC_YELLOW
		else:
			clr=CC_RED
		print(clr+F"{delta*1000:>6.1f}ms"+CC_RESET)
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

	tid_raw=tk_display.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_str=tk_display.ImageDisplayWindow(img_disp_root,"Stereo Right")
	tid_dif=tk_display.ImageDisplayWindow(img_disp_root,"Stereo Difference")
	tid_seg=tk_display.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_com=tk_display.ImageDisplayWindow(img_disp_root,"Combined")
	tid_dmd=tk_display.ImageDisplayWindow(img_disp_root,"Depth/MD")
	tid_dcv=tk_display.ImageDisplayWindow(img_disp_root,"Depth/CV")
	tid_dpsm=tk_display.ImageDisplayWindow(img_disp_root,"Depth/PSM")
	tid_digev=tk_display.ImageDisplayWindow(img_disp_root,"Depth/IGEV")


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

null_dm=numpy.ma.masked_equal(np.zeros((320,480),float),0)
# Display function
frmN=0
def display(img,*,stereo_right=None):
	global frmN
	frmN+=1
	print(CC_BOLD+CC_GREEN+F"\n### Frame {frmN} ###"+CC_RESET)
	
	if arguments.output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	

	timer.start("Segmentation")
	# Segmentation
	segs=yolodriver.segment(img)
	
	# Depth estimation
	if arguments.stereo_solvers["monodepth"]:
		timer.start("MonoDepth")
		md_raw=monodepth_driver.estimate_depth(img,depth_multiplier=0.3)
		# Restore aspect ratio
		img_smallsize=maths.fit(img.size,(480,320))
		depth_monodepth=maths.resize_matrix(md_raw,(img_smallsize[1],img_smallsize[0]))
	else:
		depth_monodepth=null_dm
	
	if stereo_right is not None:
		if arguments.stereo_solvers["opencv"]:
			timer.start("OpenCV")
			stereo_left=img
			depth_opencv=stereo.stereo_calculate(
				left=stereo_left,right=stereo_right,
				depth_multiplier=700) #MAGIC: Depth correction factor
			if hasattr(depth_opencv,"count"): # Only has it if MaskedArray
				print("OpenCV valid pixels: {}/{}".format(depth_opencv.count(),depth_opencv.size))
		else:
			depth_opencv=null_dm

		stereo_left_rsz=maths.resize_fit(stereo_left,(480,320))
		stereo_right_rsz=maths.resize_fit(stereo_right,(480,320))

		if arguments.stereo_solvers["psm"]:
			timer.start("PSMNet")

			depth_psm = PSMNet.psm.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=40) #MAGIC: Depth correction factor
		else:
			depth_psm=null_dm

		if arguments.stereo_solvers["igev"]:
			timer.start("IGEV")
			depth_igev = igev.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=50) #MAGIC: Depth correction factor
		else:
			depth_igev=null_dm
	

	timer.start("SegDepth Calculate")
	# Combine
	depth=depth_monodepth #TODO intelligent depth combining
	if depth_opencv is not None:
		depth=depth_opencv
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
	
	timer.start("Visualize")
	# Visualize Segdepths
	seg_vis=visualizations.visualize_segmentations(segs,img.size)
	combined_vis=visualizations.visualize_segdepth(segdepths_valid,img.size,img)
	dvis_md=visualizations.visualize_matrix(
		depth_monodepth,"MonoDepth")
	dvis_cv=visualizations.visualize_matrix(
		depth_opencv,"OpenCV",clip_percentiles=(5,95))
	dvis_psm=visualizations.visualize_matrix(
		depth_psm,"PSMNet",clip_percentiles=(5,95))
	dvis_igev=visualizations.visualize_matrix(
		depth_igev,"IGEV",clip_percentiles=(5,85))
	if stereo_right is not None:
		str_dif=PIL.ImageChops.difference(img,stereo_right)

	timer.start("Output")
	# Output
	if arguments.output=="tk":
		tid_raw.set_image(img)
		if stereo_right is not None:
			tid_str.set_image(stereo_right)
			tid_dif.set_image(str_dif)
		tid_seg.set_image(seg_vis)
		tid_com.set_image(combined_vis)
		tid_dmd.set_image(dvis_md)
		tid_dcv.set_image(dvis_cv)
		tid_dpsm.set_image(dvis_psm)
		tid_digev.set_image(dvis_igev)
	elif arguments.output=="web":
		# Raw frames
		st.put_image("/raw.jpg",img)
		if stereo_right is not None:
			st.put_image("/str.jpg",stereo_right)
			st.put_image("/dif.jpg",str_dif)
			
		# Segmentations
		st.put_image("/seg.jpg",seg_vis)
		st.put_image("/com.jpg",combined_vis)
		st.put_string("/information",str(frmN))
		
		objects_json=combined.segdepths_to_json(segdepths_valid,img)
		st.put_json("/objects",objects_json)
		
		# Depths
		st.put_json("/pc_monodepth.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_monodepth,
				color_image=img,
				sampleN=5000))
		st.put_image("/dmd.jpg",dvis_md)
		
		st.put_json("/pc_opencv.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_opencv,
				color_image=img,
				sampleN=5000))
		st.put_image("/dcv.jpg",dvis_cv)
		
		st.put_json("/pc_psmnet.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_psm,
				color_image=img,
				sampleN=5000))
		st.put_image("/dpsm.jpg",dvis_psm)

		st.put_json("/pc_igev.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_igev,
				color_image=img,
				sampleN=5000))
		st.put_image("/digev.jpg",dvis_igev)
		
		#st.put_image("/dcm.jpg",compare_vis)
		
		st.put_string("/update_flag",str(random.random()))
		
	elif arguments.output=="file":
		img.save("out/img.jpg")
		if stereo_right is not None:
			stereo_right.save("out/stereo_right.jpg")
			str_dif.save("out/str_dif.jpg")
		seg_vis.save("out/seg_vis.jpg")
		combined_vis.save("out/combined_vis.jpg")
		dvis_md.save("out/dvis_md.jpg")
		dvis_cv.save("out/dvis_cv.jpg")
		dvis_psm.save("out/dvis_psm.jpg")
		dvis_igev.save("out/dvis_igev.jpg")
	timer.start("Get Frame")
		
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
			display(pimL,stereo_right=pimR)
			if arguments.singleframe: break
	elif arguments.source=="image":
		while True:
			display(PIL.Image.open(arguments.infile))
			if arguments.singleframe: break
	elif arguments.source=="image_stereo":
		while True:
			iL=PIL.Image.open(arguments.infileL).convert("RGB")
			iR=PIL.Image.open(arguments.infileR).convert("RGB")
			display(iL,stereo_right=iR)
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
	
	else:
		print("how are you here")
		0/0

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
