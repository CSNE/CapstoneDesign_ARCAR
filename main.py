
# Arguments parse
import arguments


# Imports
# Standard Library
import time


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
if arguments.source=="video":
	import video
if arguments.output=="web":
	import web
import maths
import combined
if arguments.source=="kinect":
	import kinect
import visualizations


# Make YOLO quiet
import ultralytics.yolo.utils
import logging
ultralytics.yolo.utils.LOGGER.setLevel(logging.WARNING)
if arguments.verblevel>2:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.INFO)
if arguments.verblevel>3:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.DEBUG)


## GUI Setup
if arguments.output=="tk":
	img_disp_root=tk_display.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	tid_hud_seg=tk_display.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_camraw=tk_display.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_depth=tk_display.ImageDisplayWindow(img_disp_root,"Depth Estimation")
	tid_combined=tk_display.ImageDisplayWindow(img_disp_root,"Combined")

# Web Server setup
if arguments.output=="web":
	server_port=28301
	st=web.ServerThread(server_port)
	st.start()
	with open("webpage.html","rb") as f:
		page=f.read()
	st.put_data("/",page)
	with open("webpage.js","rb") as f:
		page=f.read()
	st.put_data("/webpage.js",page,"text/javascript")
	time.sleep(0.2)

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

# Display function
frmN=0
def display(img,dep=None):
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
	if dep is None:
		# Depth estimation
		dep=monodepth_driver.estimate_depth(img,depth_multiplier=0.2)
	dvis=visualizations.visualize_matrix(dep)
	

	timer.start("Combining")
	# Combine
	segdepths_raw=combined.calculate_segdepth(segs,dep)

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
		tid_depth.set_image(dvis)
		tid_combined.set_image(combined_vis)
	elif arguments.output=="web":
		st.put_image("/raw.jpg",img)
		st.put_image("/seg.jpg",seg_vis)
		st.put_image("/dep.jpg",dvis)
		st.put_image("/com.jpg",combined_vis)
		st.put_string("/information",str(frmN))
		objects_json=combined.segdepths_to_json(segdepths_valid,img)
		st.put_json("/objects",objects_json)
	elif arguments.output=="file":
		img.save("out_raw.jpg")
		seg_vis.save("out_seg.jpg")
		dvis.save("out_dep.jpg")
		combined_vis.save("out_com.jpg")
	timer.start("Get Frame")


# Main capture loop
def capture_loop():
	if arguments.source=="webcam":
		camera=cv2.VideoCapture(arguments.wc)
		while True:
			res,img=camera.read()
			if not res:
				print("Cam read {} failed!".format(arguments.wc))
				break
			pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
			display(pim)
			if arguments.singleframe: break
	elif arguments.source=="kinect":
		k4a=kinect.getK4A(arguments.kinect_rgb,arguments.kinect_depth,arguments.kinect_fps)
		k4a.start()
		while True:
			kcd=kinect.getCap(k4a)
			display(kcd.color_image,kcd.depth_data_mapped)
			if arguments.singleframe: break
	elif arguments.source=="image":
		while True:
			display(PIL.Image.open(arguments.infile))
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

try:
	capture_loop()
except KeyboardInterrupt:
	print("^C Received. Exiting...")
finally:
	if arguments.output=="web":
		st.die()
print("Main thread terminated.")
