
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

	tid_raw=tk_display.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_str=tk_display.ImageDisplayWindow(img_disp_root,"Stereo Right")
	tid_dif=tk_display.ImageDisplayWindow(img_disp_root,"Stereo Difference")
	tid_seg=tk_display.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_com=tk_display.ImageDisplayWindow(img_disp_root,"Combined")
	tid_dmd=tk_display.ImageDisplayWindow(img_disp_root,"Depth/MD")
	tid_dcv=tk_display.ImageDisplayWindow(img_disp_root,"Depth/CV")
	tid_dpsm=tk_display.ImageDisplayWindow(img_disp_root,"Depth/PSM")


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
def display(img,*,stereo_right=None):
	global frmN
	frmN+=1
	print(F"\nFrame {frmN}")
	
	if arguments.output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	

	timer.start("Segmentation")
	# Segmentation
	segs=yolodriver.segment(img)
	
	# Depth estimation
	timer.start("MonoDepth")
	depth_monodepth=monodepth_driver.estimate_depth(img,depth_multiplier=0.3)
	
	if stereo_right is not None:
		timer.start("OpenCV")
		stereo_left=img
		depth_opencv=stereo.stereo_calculate(
			left=stereo_left,right=stereo_right,
			depth_multiplier=1000) #MAGIC: Depth correction factor
		if hasattr(depth_opencv,"count"): # Only has it if MaskedArray
			print("OpenCV valid pixels: {}/{}".format(depth_opencv.count(),depth_opencv.size))
		
		timer.start("PSMNet")
		stereo_left_rsz=maths.resize_fit(stereo_left,(480,320))
		stereo_right_rsz=maths.resize_fit(stereo_right,(480,320))
		depth_psm = PSMNet.psm.calculate(
			left=stereo_left_rsz,
			right=stereo_right_rsz,
			depth_multiplier=40) #MAGIC: Depth correction factor
	

	timer.start("SegDepth Calculate")
	# Combine
	depth=depth_monodepth #TODO intelligent depth combining
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
		depth_psm,"PSMNet")
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
				sampleN=3000))
		st.put_image("/dmd.jpg",dvis_md)
		
		st.put_json("/pc_opencv.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_opencv,
				color_image=img,
				sampleN=3000))
		st.put_image("/dcv.jpg",dvis_cv)
		
		st.put_json("/pc_psmnet.json",
			webdata.depthmap_to_pointcloud_json(
				depth_map=depth_psm,
				color_image=img,
				sampleN=3000))
		st.put_image("/dpsm.jpg",dvis_psm)
		
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
