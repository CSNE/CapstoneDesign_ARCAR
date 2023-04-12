# Arguments Parsing
import argparse
import sys

ap=argparse.ArgumentParser(
	description="ARCAR Python Program")

# Required
ap.add_argument(
	"--source","-src",
	choices=["webcam","image","video","screenshot","kinect"],
	required=True)
ap.add_argument(
	"--output","-o",
	choices=["tk","web","file","nothing"],
	required=True)

# Per-Input
ap.add_argument(
	"--webcam-number","-wc",
	type=int,
	default=0)
ap.add_argument(
	"--input-file","-i")
ap.add_argument(
	"--video-speed","-vs",
	type=float,
	default=1.0)
ap.add_argument(
	"--screenshot-region","-sr")
ap.add_argument(
	"--kinect-depth","-kd",
	choices=[
		'NFOV_2X2BINNED', "nb",
		'NFOV_UNBINNED', "nu",
		'WFOV_2X2BINNED', "wb",
		'WFOV_UNBINNED', "wu"],
	default="NFOV_UNBINNED")
ap.add_argument(
	"--kinect-rgb","-kr",
	choices=[
		'RES_720P',  "720",
		'RES_1080P', "1080",
		'RES_1440P', "1440",
		'RES_1536P', "1536",
		'RES_2160P', "2160",
		'RES_3072P', "3072"],
	default="RES_720P")
ap.add_argument(
	"--kinect-fps","-kf",
	choices=["5","15","30"],
	default="15")

# Optional
ap.add_argument(
	"--single-frame","-sf",
	action="store_true")
ap.add_argument(
	'--verbose', '-v',
	action='count',
	default=0)

args=ap.parse_args()

arg_source=args.source
arg_wc=args.webcam_number
arg_vs=args.video_speed
if arg_source in ("image","video"):
	if "input_file" not in args:
		print("For image or video input, you need to supply the input file.")
		print("( --input-file=FILE or -f FILE )")
		sys.exit(1)
	else:
		arg_infile=args.input_file
if args.screenshot_region is not None:
	
	spl=args.screenshot_region.split(",")
	try:
		if len(spl) != 4:
			raise ValueError
		arg_sr=[int(i) for i in spl]
	except ValueError:
		print("--screenshot-region must be 4 integers, separated by commas without spaces")
		sys.exit(1)
else:
	arg_sr=None
		
arg_output=args.output
arg_singleframe=args.single_frame

arg_verblevel=args.verbose




# Imports
# Standard Library
import time

# 3rd party
import PIL.Image
import PIL.ImageGrab
import cv2
import numpy as np

# Local modules
if arg_output=="tk":
	import gui
import ai
import depth
import video
if arg_output=="web":
	import web
import maths
import combined
if arg_source=="kinect":
	import kinect
	arg_kinect_depth={
		'NFOV_2X2BINNED':kinect.DepthMode.NFOV_2X2BINNED,
		"nb":kinect.DepthMode.NFOV_2X2BINNED,
		'NFOV_UNBINNED':kinect.DepthMode.NFOV_UNBINNED,
		"nu":kinect.DepthMode.NFOV_UNBINNED,
		'WFOV_2X2BINNED':kinect.DepthMode.WFOV_2X2BINNED,
		"wb":kinect.DepthMode.WFOV_2X2BINNED,
		'WFOV_UNBINNED':kinect.DepthMode.WFOV_UNBINNED,
		"wu":kinect.DepthMode.WFOV_UNBINNED
		}[args.kinect_depth]
	arg_kinect_rgb={
		'RES_720P':kinect.ColorResolution.RES_720P,
		"720":kinect.ColorResolution.RES_720P,
		'RES_1080P':kinect.ColorResolution.RES_1080P,
		"1080":kinect.ColorResolution.RES_1080P,
		'RES_1440P':kinect.ColorResolution.RES_1440P,
		"1440":kinect.ColorResolution.RES_1440P,
		'RES_1536P':kinect.ColorResolution.RES_1536P,
		"1536":kinect.ColorResolution.RES_1536P,
		'RES_2160P':kinect.ColorResolution.RES_2160P,
		"2160":kinect.ColorResolution.RES_2160P,
		'RES_3072P':kinect.ColorResolution.RES_3072P,
		"3072":kinect.ColorResolution.RES_3072P
		}[args.kinect_rgb]
	arg_kinect_fps={
		"5":kinect.FPS.FPS_5,
		"15":kinect.FPS.FPS_15,
		"30":kinect.FPS.FPS_30
		}[args.kinect_fps]


# Make YOLO quiet
import ultralytics.yolo.utils
import logging
ultralytics.yolo.utils.LOGGER.setLevel(logging.WARNING)
if arg_verblevel>2:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.INFO)
if arg_verblevel>3:
	ultralytics.yolo.utils.LOGGER.setLevel(logging.DEBUG)


## GUI Setup
if arg_output=="tk":
	img_disp_root=gui.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	#tid_hud_det=gui.ImageDisplayWindow(img_disp_root,"Detection")
	tid_hud_seg=gui.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_camraw=gui.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_depth=gui.ImageDisplayWindow(img_disp_root,"Depth Estimation")
	tid_combined=gui.ImageDisplayWindow(img_disp_root,"Combined")

# Web Server setup
if arg_output=="web":
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


# Global variables
de=depth.DepthEstimator()

# Display function
frmN=0
def display(img,dep=None):
	global frmN
	frmN+=1
	
	if arg_output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	
	# Segmentation
	segs=ai.segment(img)
	seg_vis=ai.visualize_segmentation(segs,img.size)
	
	if dep is None:
		# Depth estimation
		dep=de.estimate(img,depth_multiplier=0.2)
	dvis=depth.visualize_depth(dep)
	
	# Combine
	segdepths=combined.calculate_segdepth(segs,dep)
	all_segs=len(segdepths)
	segdepths=[i for i in segdepths if i.depth_valid]
	filtered_segdepths=len(segdepths)
	print(F"Filtered {all_segs-filtered_segdepths} out SegDepths out of {all_segs} because it has no depth data.")
	combined_vis=combined.visualize_segdepth(segdepths,img.size,img)
	
	# Output
	if arg_output=="tk":
		tid_camraw.set_image(img)
		tid_hud_seg.set_image(seg_vis)
		tid_depth.set_image(dvis)
		tid_combined.set_image(combined_vis)
	elif arg_output=="web":
		st.put_image("/raw.jpg",img)
		st.put_image("/seg.jpg",seg_vis)
		st.put_image("/dep.jpg",dvis)
		st.put_image("/com.jpg",combined_vis)
		st.put_string("/information",str(frmN))
		objects_json=combined.segdepths_to_json(segdepths,img)
		st.put_json("/objects",objects_json)
	elif arg_output=="file":
		img.save("out_raw.jpg")
		seg_vis.save("out_seg.jpg")
		dvis.save("out_dep.jpg")
		combined_vis.save("out_com.jpg")
		

# Main capture loop
def capture_loop():
	if arg_source=="webcam":
		camera=cv2.VideoCapture(arg_wc)
		while True:
			res,img=camera.read()
			if not res:
				print("Cam read {} failed!".format(arg_wc))
				break
			pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
			display(pim)
			if arg_singleframe: break
	elif arg_source=="kinect":
		k4a=kinect.getK4A(arg_kinect_rgb,arg_kinect_depth,arg_kinect_fps)
		k4a.start()
		while True:
			kcd=kinect.getCap(k4a)
			display(kcd.color_image,kcd.depth_data_mapped)
			if arg_singleframe: break
	elif arg_source=="image":
		while True:
			display(PIL.Image.open(arg_infile))
			if arg_singleframe: break
	elif arg_source=="video":
		startT=time.time()
		while True:
			vt=(time.time()-startT)*arg_vs
			vf=video.get_video_frame(arg_infile,vt)
			display(vf)
			if arg_singleframe: break

	elif arg_source=="screenshot":
		while True:
			display(PIL.ImageGrab.grab(arg_sr))
			if arg_singleframe: break

try:
	capture_loop()
except KeyboardInterrupt:
	print("^C Received. Exiting...")
finally:
	if arg_output=="web":
		st.die()
print("Main thread terminated.")
