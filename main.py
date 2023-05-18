
# Arguments parse
import arguments

# Terminal colors setup
import platform
if platform.system()=="Windows":
	import os
	import ansi
	os.system("color") #enable color on Windows
	print("Enabled "+ansi.CYAN+ansi.BOLD+"COLOR"+ansi.RESET)
import ansi


# Supress warnings
import warnings
if arguments.verblevel<2:
	print(ansi.YELLOW+ansi.BOLD+"Supressing all warnings!"+ansi.RESET)
	warnings.filterwarnings("ignore")


# Timer
import sequence_timer
import_timer=sequence_timer.SequenceTimer(
	orange_thresh=0.5,red_thresh=2.0,	
	prefix="Import")


# Imports
print("\nImporting everything...")
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

import_timer.split(starting="Numpy")
import numpy
import numpy.ma

import_timer.split(starting="OpenCV")
import cv2

import_timer.split(starting="PyTorch")
import torch


# Local modules
if arguments.cuda:
	if not torch.cuda.is_available():
		print("CUDA option was set but torch.cuda.is_available() is False")
		sys.exit(1)

if arguments.debug_output=="tk":
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
	

import_timer.split(starting="Web")
import web
import webdata

import_timer.split(starting="misc")
import maths
import coordinates
import combined
import visualizations
import stereo_playback
import building_detect
import magic

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
import_timer.split()

print("\nSetup...")
## Setup
setup_timer=sequence_timer.SequenceTimer(
	orange_thresh=0.5,red_thresh=2.0,	
	prefix="Setup")
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
if arguments.debug_output=="tk":
	setup_timer.split(starting="Tk")
	img_disp_root=tk_display.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(magic.system.tk_initialize_wait) # Race condition

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

setup_timer.split(starting="Webserver")
server_port=magic.web.server_port
st=web.ServerThread(server_port)
st.start()
cleanup_functions.append(lambda:st.die())
web_url=F"http://localhost:{server_port}"

with open("mainpage.html","rb") as f:
	page=f.read()
st.put_data("/main.html",page)
with open("mainpage.js","rb") as f:
	page=f.read()
st.put_data("/mainpage.js",page,"text/javascript")
with open("helvetiker_regular.typeface.json","rb") as f:
	fnt=f.read()
st.put_data("/font.typeface.json",fnt)
print("Main page active at "+ansi.GREEN+ansi.BOLD+web_url+"/main.html"+ansi.RESET)

if arguments.debug_output=="web":
	with open("webpage.html","rb") as f:
		page=f.read()
	st.put_data("/debug.html",page)
	
	with open("webpage.js","rb") as f:
		page=f.read()
	st.put_data("/webpage.js",page,"text/javascript")
	
	print("Debug page active at "+ansi.GREEN+ansi.BOLD+web_url+"/debug.html"+ansi.RESET)
setup_timer.split()


print("\nStart Loop...")
null_dm=numpy.ma.masked_equal(numpy.zeros((320,480),float),0)
# Display function
frmN=0
loop_timer=sequence_timer.SequenceTimer(
	prefix="Frameloop",
	orange_thresh=0.1,red_thresh=0.3)
frame_timer=sequence_timer.SequenceTimer(
	prefix="Frame Total Time > ",
	orange_thresh=0.3,red_thresh=1.0)
def display(img,*,stereo_right=None,frame_name=None):
	global frmN
	frmN+=1
	pad=" "*2+"#"*8+" "*2
	print("\n"+ansi.BOLD+ansi.BLUE+pad+F"Frame {frmN:>4d}"+pad+ansi.RESET)
	if frame_name:
		print(ansi.BLUE+""+frame_name+ansi.RESET)
	frame_timer.split()
	loop_timer.split(ending="(Frame Acquisition)")
	if arguments.debug_output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	

	loop_timer.split(starting="Segmentation")
	# Segmentation
	segs=yolodriver.segment(img,use_cuda=arguments.cuda)
	
	# Depth estimation
	if arguments.stereo_solvers["monodepth"]:
		loop_timer.split(starting="MonoDepth")
		md_raw=md_de.estimate(img,depth_multiplier=magic.monodepth.multiplier)
		# Restore aspect ratio
		img_smallsize=maths.fit(img.size,(480,320))
		depth_monodepth=maths.resize_matrix(md_raw,(img_smallsize[1],img_smallsize[0]))
	else:
		depth_monodepth=None
		
	if stereo_right is not None:
		stereo_left=img
		if arguments.stereo_solvers["opencv"]:
			loop_timer.split(starting="OpenCV")
			depth_opencv=stereo.stereo_calculate(
				left=stereo_left,right=stereo_right,
				depth_multiplier=magic.opencv.multiplier) 
			if hasattr(depth_opencv,"count"): # Only has it if MaskedArray
				pass#print("OpenCV valid pixels: {}/{}".format(depth_opencv.count(),depth_opencv.size))
		else:
			depth_opencv=None
			
		stereo_left_rsz=maths.resize_fit(stereo_left,arguments.solve_resize)
		stereo_right_rsz=maths.resize_fit(stereo_right,arguments.solve_resize)

		if arguments.stereo_solvers["psm"]:
			loop_timer.split(starting="PSMNet")
			depth_psm = psmnet.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=magic.psm.multiplier).astype(float)
		else:
			depth_psm=None

		if arguments.stereo_solvers["igev"]:
			loop_timer.split(starting="IGEV")
			depth_igev = igev.calculate(
				left=stereo_left_rsz,
				right=stereo_right_rsz,
				depth_multiplier=magic.igev.multiplier) 
		else:
			depth_igev=None
	else:
		depth_opencv=None
		depth_psm=None
		depth_igev=None


	# Get the first non-null entry in the list - maybe make this smarter
	depth=next(filter(
		lambda x: x is not None,
		[depth_igev,depth_opencv,depth_psm,depth_monodepth]))
	
	ss2rsm_image=coordinates.ScreenSpaceToRealSpaceMapper(
		image_width=img.width,image_height=img.height,
		reference_distance=magic.mapping.reference_distance,
		reference_width=magic.mapping.reference_width)
	ss2rsm_depthmap=coordinates.ScreenSpaceToRealSpaceMapper(
		image_width=depth.shape[1],image_height=depth.shape[0],
		reference_distance=magic.mapping.reference_distance,
		reference_width=magic.mapping.reference_width)
	
	
	loop_timer.split(starting="Seg3D Calculate")
	
	seg3ds=combined.segments_depth_combine(
		segments=segs,
		sstrsm=ss2rsm_image,
		depthmap=depth,
		normal_sample_offset=None)
	
	
	if arguments.detect_walls:
		loop_timer.split(starting="Detect building")
		depth_blurred=maths.gaussian_blur(depth,magic.walls.blur_sdev)
		walls_unfiltered=building_detect.get_fit_candidates(
			depth_blurred,
			magic.walls.random_samples,
			magic.walls.derivative_radius,
			ss2rsm_depthmap)
		
		walls=[i for i in walls_unfiltered if i.match_ratio>magic.walls.match_threshold] #MAGIC: match thresh
		print(F"{len(walls)} walls detected.                     ")
		'''
		for i in range(len(walls[:4])):
			print(i)
			print("  ",walls[i].match_ratio)
			print("  ",walls[i].plane_definition)
			print("  ",walls[i].normal_vector)
			print("  ",walls[i].center_real)'''
	
	if arguments.debug_output != "nothing":
		loop_timer.split(starting="Segment visuals")
		# Visualize Segdepths
		seg_vis=visualizations.visualize_segmentations(segs,img.size)
		
		loop_timer.split(starting="SegDepth Visuals")
		combined_vis=visualizations.visualize_seg3d(seg3ds,img.size,img)
		
		loop_timer.split(starting="Matrix Visuals")
		if arguments.stereo_solvers["monodepth"]:
			dvis_md=visualizations.visualize_matrix(
				depth_monodepth,"MonoDepth")
		if arguments.stereo_solvers["opencv"]:
			dvis_cv=visualizations.visualize_matrix(
				depth_opencv,"OpenCV",clip_percentiles=(5,95))
		if arguments.stereo_solvers["psm"]:
			dvis_psm=visualizations.visualize_matrix(
				depth_psm,"PSMNet",clip_percentiles=(5,95))
		if arguments.stereo_solvers["igev"]:
			dvis_igev=visualizations.visualize_matrix(
				depth_igev,"IGEV",clip_percentiles=(5,85))
		if stereo_right is not None:
			str_dif=PIL.ImageChops.difference(img,stereo_right)
		
		if arguments.detect_walls:
			wvis_blurred_depth=visualizations.visualize_matrix(
				depth_blurred,"Depth Blurred",clip_percentiles=(5,95))
			wvis_error=[None]*4
			wvis_mask=[None]*4
			wvis_maskpc=[None]*4
			if arguments.do_wall_visual:
				for i in range(4):
					if i<len(walls_unfiltered):
						wall=walls_unfiltered[i]
						wvis_error[i]=(visualizations.visualize_matrix(
							wall.error,F"Wall {i} Error",
							clip_values=(-2,+2),cmap="seismic",
							annotate_point=coordinates.Coordinates2D(
								x=wall.plane_definition.originX,
								y=wall.plane_definition.originY)))
						wvis_mask[i]=(visualizations.visualize_matrix(
							wall.mask,F"Wall {i} Mask (Ratio={wall.match_ratio*100:.1f}%)",
							cmap="Greys",
							annotate_point=wall.center_map))
						wvis_maskpc[i]=(visualizations.visualize_matrix(
							wall.mask_prechoke,F"Wall {i} Pre-Choke Mask",
							cmap="Greys",
							annotate_point=wall.center_map))

		

		
		# Output
		if arguments.debug_output=="tk":
			loop_timer.split(starting="Tk update")
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
		elif arguments.debug_output=="web":
			if arguments.pointcloud:
				loop_timer.split(starting="Debug Point Cloud")
				if arguments.stereo_solvers["monodepth"]:
					pc_monodepth=webdata.depthmap_to_pointcloud_json(
						depth_map=depth_monodepth,mapper=ss2rsm_image,
						color_image=img,
						sampleN=magic.visuals.debug_pointcloud_count)
					st.put_json("/pc_monodepth.json",pc_monodepth)
				if arguments.stereo_solvers["opencv"]:
					pc_opencv=webdata.depthmap_to_pointcloud_json(
						depth_map=depth_opencv,mapper=ss2rsm_image,
						color_image=img,
						sampleN=magic.visuals.debug_pointcloud_count)
					st.put_json("/pc_opencv.json",pc_opencv)
				if arguments.stereo_solvers["psm"]:
					pc_psmnet=webdata.depthmap_to_pointcloud_json(
						depth_map=depth_psm,mapper=ss2rsm_image,
						color_image=img,
						sampleN=magic.visuals.debug_pointcloud_count)
					st.put_json("/pc_psmnet.json",pc_psmnet)
				if arguments.stereo_solvers["igev"]:
					pc_igev=webdata.depthmap_to_pointcloud_json(
						depth_map=depth_igev,mapper=ss2rsm_image,
						color_image=img,
						sampleN=magic.visuals.debug_pointcloud_count)
					st.put_json("/pc_igev.json",pc_igev)
			
			loop_timer.split(starting="Update Debug Page")
			# Raw frames
			st.put_image("/raw.jpg",img)
			if stereo_right is not None:
				st.put_image("/str.jpg",stereo_right)
				st.put_image("/dif.jpg",str_dif)
				
			# Segmentations
			st.put_image("/seg.jpg",seg_vis)
			st.put_image("/com.jpg",combined_vis)
			if frame_name is None:
				st.put_string("/information",str(frmN))
			else:
				st.put_string("/information",str(frame_name))
			
			# Depths
			if arguments.stereo_solvers["monodepth"]:
				st.put_image("/dmd.jpg",dvis_md)
			if arguments.stereo_solvers["opencv"]:
				st.put_image("/dcv.jpg",dvis_cv)
			if arguments.stereo_solvers["psm"]:
				st.put_image("/dpsm.jpg",dvis_psm)
			if arguments.stereo_solvers["igev"]:
				st.put_image("/digev.jpg",dvis_igev)
				
			# Wall
			if arguments.detect_walls:
				st.put_image("/wblur.jpg",wvis_blurred_depth)
				for i in range(4):
					if wvis_error[i] is not None:
						st.put_image(F"/werr{i}.jpg",wvis_error[i])
						st.put_image(F"/wmsk{i}.jpg",wvis_mask[i])
						st.put_image(F"/wmpc{i}.jpg",wvis_maskpc[i])
					else:
						st.clear_data(F"/werr{i}.jpg")
						st.clear_data(F"/wmsk{i}.jpg")
						st.clear_data(F"/wmpc{i}.jpg")

		elif arguments.debug_output=="file":
			loop_timer.split(starting="File output save")
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
	
	loop_timer.split(starting="Update Main Page")
	seg3d_json=webdata.seg3d_to_json(
		seg3ds,use_flat=arguments.flatten_segments)
	st.put_json("/seg3d",seg3d_json)
	seg3dText_json=webdata.seg3d_to_text_json(
		seg3ds,use_flat=arguments.flatten_segments)
	st.put_json("/texts",seg3dText_json)
	if arguments.pointcloud:
		loop_timer.split(starting="Mainpage Point Cloud")
		pc_main=webdata.depthmap_to_pointcloud_json(
			depth_map=depth,mapper=ss2rsm_image,
			color_image=img,
			sampleN=magic.visuals.mainpage_pointcloud_count)
		st.put_json("/pointcloud",pc_main)
	if arguments.detect_walls:
		wj=webdata.wall_to_json(walls)
		st.put_json("/walls",wj)
	
	st.put_string("/update_flag",str(random.random()))
	
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
	elif arguments.source=="stereo_playback":
		sp=stereo_playback.StereoPlayback(arguments.infile)
		
		force_refresh=False
		def pch(q):
			nonlocal force_refresh
			if "type" in q:
				t=q["type"][0]
				print("Browser command:",t)
				if t=="pause": sp.stop()
				elif t=="rewind": sp.rewind()
				elif t=="play": sp.play()
				elif t=="+1": sp.delta_frame(+1)
				elif t=="-1": sp.delta_frame(-1)
				elif t=="+10": sp.delta_frame(+10)
				elif t=="-10": sp.delta_frame(-10)
				elif t=="+100": sp.delta_frame(+100)
				elif t=="-100": sp.delta_frame(-100)
				elif t=="reload": force_refresh=True
				elif t=="rand": sp.randframe()
			elif "jumpTo" in q:
				jt=int(q["jumpTo"][0])
				print("Jump frame:",jt)
				sp.set_frame(jt)

		st.set_handler("/playbackControl",pch)
		
		last_fidx=None
		while True:
			sp.update()
			if (not force_refresh) and (sp.frameindex == last_fidx):
				time.sleep(0.01)
				continue
			# Refreshing!
			force_refresh=False
			framepath=sp.get_frame_fp()[0]
			#print("Read frame",framepath)
			last_fidx=sp.frameindex
			if sp.over():
				break
			iL,iR=sp.get_frame()
			display(iL,stereo_right=iR,
				frame_name=framepath)
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
