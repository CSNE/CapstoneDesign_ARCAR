# Options

import argparse
import sys

ap=argparse.ArgumentParser(
	description="ARCAR Python Program")
ap.add_argument(
	"--source","-src",
	choices=["webcam","image","video"],
	required=True)
ap.add_argument(
	"--input-file","-i")
ap.add_argument(
	"--webcam-number","-wc",
	default=0)
ap.add_argument(
	"--video-speed","-vs",
	type=float,
	default=1.0)
ap.add_argument(
	"--output","-o",
	choices=["tk","web","file","nothing"],
	required=True)

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
		
arg_output=args.output

# Standard Library
import time

# 3rd party
import PIL.Image
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


font=PIL.ImageFont.truetype("/usr/share/fonts/TTF/Hack-Bold.ttf",size=36)
de=depth.DepthEstimator()

def display(img):
	if arg_output=="tk":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
	
	# Segmentation
	segs=ai.segment(img)
	for s in segs:
		print(F"X{s.xmin:.0f}-{s.xmax:.0f} Y{s.ymin:.0f}-{s.ymax:.0f} C{s.confidence:.3f} {s.name}")
	seg_vis=ai.visualize_segmentation(segs,img.size)
	
	# Depth estimation
	dep=de.estimate(img)
	dvis=depth.visualize_depth(dep)
	
	# Combine
	combined_vis=PIL.Image.new("RGB",img.size)
	draw=PIL.ImageDraw.Draw(combined_vis)
	objects_json=[]
	for s in segs:
		
		area_bool=~s.area.astype(bool)
		
		# Resize depth map to area map
		dep_rsz=maths.resize_matrix(dep,s.area.shape)
		
		# Masked array
		masked_depth=np.ma.MaskedArray(dep_rsz,mask=area_bool)
		depth_mean=masked_depth.mean()
		
		print(F"{s.name} {s.confidence:.3f} {depth_mean:.1f}m")
		
		bbox_center_X=(s.xmin+s.xmax)/2
		bbox_size_X=s.xmax-s.xmin
		bbox_center_Y=(s.ymin+s.ymax)/2
		bbox_size_Y=s.ymax-s.ymin
		shp=s.area.shape
		
		for i in range(len(s.points)):
			j=i-1
			startX=s.points[i][0]*img.width
			startY=s.points[i][1]*img.height
			endX=  s.points[j][0]*img.width
			endY=  s.points[j][1]*img.height
			draw.line((startX,startY,endX,endY),fill="#FF0000",width=3)
		draw.text((bbox_center_X,bbox_center_Y),F"{s.name}\n{depth_mean:.1f}m",
			fill="#00FFFF",font=font,anchor="ms")
		
		# 5 meters is the reference point - calibrate later
		distance_scaling_factor=depth_mean/5
		# at reference distance, how large is the screen? - again, calibrate later
		screen_dim_X=3
		screen_dim_Y=screen_dim_X/img.width*img.height
		rel_coords_X=(bbox_center_X-(img.width/2))/img.width
		actual_coords_X=rel_coords_X*screen_dim_X*distance_scaling_factor
		actual_size_X=bbox_size_X/img.width*screen_dim_X*distance_scaling_factor
		rel_coords_Y=(bbox_center_Y-(img.height/2))/img.height
		actual_coords_Y=rel_coords_Y*screen_dim_Y*distance_scaling_factor
		actual_size_Y=bbox_size_Y/img.height*screen_dim_Y*distance_scaling_factor
		#assert type(s.name) is str
		#print(type(actual_coords_X))
		obj_data={"name":str(s.name),
			 "coordX":float(actual_coords_X),
			 "coordY":float(actual_coords_Y),
			 "coordZ":float(depth_mean),
			 "sizeX":float(actual_size_X),
			 "sizeY":float(actual_size_Y)}
		for k in obj_data:
			print(k,obj_data[k])
		objects_json.append(obj_data)
	# Output
	if arg_output=="tk":
		tid_camraw.set_image(img)
		#tid_hud_det.set_image(det_vis)
		tid_hud_seg.set_image(seg_vis)
		tid_depth.set_image(dvis)
		tid_combined.set_image(combined_vis)
	elif arg_output=="web":
		st.put_image("/raw.jpg",img)
		#st.put_image("/det.jpg",det_vis)
		st.put_image("/seg.jpg",seg_vis)
		st.put_image("/dep.jpg",dvis)
		st.put_image("/com.jpg",combined_vis)
		st.put_string("/information","{:.1f}s".format(vt))
		st.put_json("/objects",objects_json)
	elif arg_output=="file":
		img.save("out_raw.jpg")
		#det_vis.save("out_det.jpg")
		seg_vis.save("out_seg.jpg")
		dvis.save("out_dep.jpg")
		combined_vis.save("out_com.jpg")
		

# Image Sources
if arg_source=="webcam":
	camera=cv2.VideoCapture(arg_wc)
	while True:
		res,img=camera.read()
		if not res:
			print("Cam read failed!")
			break
		pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		display(pim)

elif arg_source=="image":
	display(PIL.Image.open(arg_infile))
elif arg_source=="video":
	startT=time.time()
	while True:
		vt=(time.time()-startT)*arg_vs
		vf=video.get_video_frame(arg_infile,vt)
		display(vf)


print("Main thread terminated.")
