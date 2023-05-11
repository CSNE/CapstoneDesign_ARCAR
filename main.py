# Arguments parse
import arguments

# Supress warnings
import warnings
if arguments.verblevel<2:
	print("Supressing all warnings!")
	warnings.filterwarnings("ignore")


# Timer
import sequence_timer
import_timer=sequence_timer.SequenceTimer(prefix="Import")


# Imports
# Standard Library
import_timer.split(starting="Standard Library")
import time
import os.path
import os
import random
import traceback
import sys


# 3rd party
import_timer.split(starting="PIL")
import PIL.Image
import PIL.ImageGrab

import_timer.split(starting="OpenCV")
import cv2

import_timer.split(starting="Numpy")
import numpy
import numpy.ma

import_timer.split(starting="PyTorch")
import torch


# Local modules
if arguments.cuda:
	if not torch.cuda.is_available():
		print("CUDA option was set but torch.cuda.is_available() is False")
		sys.exit(1)

if arguments.output=="tk":
	import_timer.split(starting="TkDisplay")
	import tk_display

import_timer.split(starting="YOLO")
import yolodriver

if arguments.source in ("webcam","webcam_stereo"):
	import_timer.split(starting="Webcam")
	import webcam
	
if arguments.source=="video":
	import_timer.split(starting="Video")
	import video
	
if arguments.output=="web":
	import_timer.split(starting="Web")
	import web
	import webdata

import_timer.split(starting="misc")
import maths
import ansi

import_timer.split(starting="combine")
import combined

import_timer.split(starting="visualizations")
import visualizations

if arguments.stereo_solvers["opencv"]:
	import_timer.split(starting="Stereo")
	import stereo
	
if arguments.stereo_solvers["monodepth"]:
	import_timer.split(starting="MonoDepth")
	import monodepth_driver
	
if arguments.stereo_solvers["psm"]:
	import_timer.split(starting="PSMNet")
	import PSMNet.psm
	
if arguments.stereo_solvers["igev"]:
	import_timer.split(starting="IGEV")
	import IGEV_Stereo.igev


## Setup
setup_timer=sequence_timer.SequenceTimer(prefix="Setup")
setup_timer.split(starting="YOLO")

# Make YOLO quiet
import ultralytics.yolo.utils
import logging
ultralytics.yolo.utils.LOGGER.setLevel(logging.WARNING)
if arguments.verblevel>2:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.INFO)
if arguments.verblevel>3:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.DEBUG)
	
# Force-load YOLO model by predicting on a dummy image
segs=yolodriver.segment(PIL.Image.new("RGB",(64,64)),use_cuda=arguments.cuda)

if arguments.stereo_solvers["igev"]:
	setup_timer.split(starting="IGEV")
	# Setup IGEV
	igev=IGEV_Stereo.igev.IGEVDriver(
		"IGEV_Stereo/pretrained_sceneflow.pth",
		use_cuda=arguments.cuda)
	
if arguments.stereo_solvers["psm"]:
	setup_timer.split(starting="PSM")
	# Setup PSMNet
	psmnet=PSMNet.psm.PSMDriver(
		"PSMNet/pretrained_sceneflow_new.tar",
		use_cuda=arguments.cuda)
	
if arguments.stereo_solvers["monodepth"]:
	setup_timer.split(starting="MonoDepth")
	# Setup MonoDepth2
	md_de=monodepth_driver.DepthEstimator(
		use_cuda=arguments.cuda)




# Global variables

cleanup_functions=[]


## GUI Setup
if arguments.output=="tk":
	setup_timer.split(starting="Tk")
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
	setup_timer.split(starting="Webserver")
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
setup_timer.split()


null_dm=numpy.ma.masked_equal(numpy.zeros((320,480),float),0)
# Display function
frmN=0
loop_timer=sequence_timer.SequenceTimer(
	prefix="Frameloop",
	orange_thresh=0.1,red_thresh=0.3)
frame_timer=sequence_timer.SequenceTimer(
	orange_thresh=0.3,red_thresh=1.0)
def display(img,*,stereo_right=None):
	global frmN
	frmN+=1
	print(ansi.BOLD+ansi.GREEN+F"\n### Frame {frmN} ###"+ansi.RESET)
	frame_timer.split()
	loop_timer.split(ending="Frame Acquisition")
	if arguments.output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	

	loop_timer.split(starting="Segmentation")
	# Segmentation
	segs=yolodriver.segment(img,use_cuda=arguments.cuda)
	
	# Depth estimation
	if arguments.stereo_solvers["monodepth"]:
		loop_timer.split(starting="MonoDepth")
		md_raw=md_de.estimate(img,depth_multiplier=0.3)
		# Restore aspect ratio
		img_smallsize=maths.fit(img.size,(480,320))
		depth_monodepth=maths.resize_matrix(md_raw,(img_smallsize[1],img_smallsize[0]))
	else:
		depth_monodepth=null_dm
	
	if stereo_right is not None:
		if arguments.stereo_solvers["opencv"]:
			loop_timer.split(starting="OpenCV")
			stereo_left=img
			depth_opencv=stereo.stereo_calculate(
				left=stereo_left,right=stereo_right,
				depth_multiplier=700) #MAGIC: Depth correction factor
			if hasattr(depth_opencv,"count"): # Only has it if MaskedArray
				pass#print("OpenCV valid pixels: {}/{}".format(depth_opencv.count(),depth_opencv.size))
		else:
			depth_opencv=null_dm

		stereo_left_rsz=maths.resize_fit(stereo_left,(480,320))
		stereo_right_rsz=maths.resize_fit(stereo_right,(480,320))

		if arguments.stereo_solvers["psm"]:
			loop_timer.split(starting="PSMNet")

			depth_psm = psmnet.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=40) #MAGIC: Depth correction factor
		else:
			depth_psm=null_dm

		if arguments.stereo_solvers["igev"]:
			loop_timer.split(starting="IGEV")
			depth_igev = igev.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=50) #MAGIC: Depth correction factor
		else:
			depth_igev=null_dm
	

	loop_timer.split(starting="SegDepth")
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
		pass#print(F"Removed {diff} SegDepths out of {len(segdepths_raw)} because of insufficient depth data")
	
	loop_timer.split(starting="Visualize")
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

	loop_timer.split(starting="Output")
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
	loop_timer.split()
	frame_timer.split(ending=F"Frame {frmN}")
		
# Main capture loop
def capture_loop():
	loop_timer.split()
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
	print("^C Received. Exiting...              ")
except:
	traceback.print_exc()
finally:
	print("Cleanup...")
	for i in cleanup_functions:
		i()
print("Main thread terminated.")
