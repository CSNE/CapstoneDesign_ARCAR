# Options

#IMAGE_SOURCE=("WEBCAM",2) #Webcam index
#IMAGE_SOURCE=("IMGFILE","testimg.png") #Image file and path
IMAGE_SOURCE=("VIDFILE","../KakaoTalk_20230310_155831877.mp4") #Video file and path

#OUTPUT_MODE="TK"
OUTPUT_MODE="WEB"
#OUTPUT_MODE="NOTHING"
#OUTPUT_MODE="FILE"

# Objects in YOLOv8s.pt:
# person / bicycle / car / motorcycle / airplane / bus / train / truck / boat
# traffic light / fire hydrant / stop sign / parking meter / bench / bird / cat
# dog / horse / sheep / cow / elephant / bear / zebra / giraffe / backpack / umbrella
# handbag / tie / suitcase / frisbee / skis / snowboard / sports ball / kite
# baseball bat / baseball glove / skateboard / surfboard / tennis racket / bottle
# wine glass / cup / fork / knife / spoon / bowl / banana / apple / sandwich / orange
# broccoli / carrot / hot dog / pizza / donut / cake / chair / couch / potted plant
# bed / dining table / toilet / tv / laptop / mouse / remote / keyboard / cell phone
# microwave / oven / toaster / sink / refrigerator / book / clock / vase / scissors
# teddy bear / hair drier / toothbrush
TARGET_OBJECT = "car"


# Requirements:
# YOLOv8 from ultralytics
# pillow
# openCV-python
# numpy
# tkinter (from Python standard library)

# Probably won't run in a virtual enviornment, due to it requiring tkinter.

# Standard Library
import time
import webbrowser

# 3rd party
import PIL.Image
import cv2
import numpy as np

# Local modules
import gui
import ai
import depth
import video
import web
import maths

## GUI Setup
if OUTPUT_MODE=="TK":
	img_disp_root=gui.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	tid_hud_det=gui.ImageDisplayWindow(img_disp_root,"Detection")
	tid_hud_seg=gui.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_camraw=gui.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_depth=gui.ImageDisplayWindow(img_disp_root,"Depth Estimation")
	tid_combined=gui.ImageDisplayWindow(img_disp_root,"Combined")

de=depth.DepthEstimator()

if OUTPUT_MODE=="WEB":
	server_port=28301
	st=web.ServerThread(server_port)
	st.start()
	with open("webpage.html","rb") as f:
		page=f.read()
	st.put_data("/",page)
	time.sleep(0.2)
	webbrowser.open("localhost:{}".format(server_port))


def display(img):
	if OUTPUT_MODE=="TK":
		if img_disp_root.opt_mirror:
			img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)
			
	dets=ai.detect(img)
	for d in dets:
		print(F"X{d.xmin:.0f}-{d.xmax:.0f} Y{d.ymin:.0f}-{d.ymax:.0f} C{d.confidence:.3f} {d.name}")
	det_vis=ai.visualize_detections(dets,img.size)

	segs=ai.segment(img)
	for s in segs:
		print(F"X{s.xmin:.0f}-{s.xmax:.0f} Y{s.ymin:.0f}-{s.ymax:.0f} C{s.confidence:.3f} {s.name}")
	seg_vis=ai.visualize_segmentation(segs,img.size)

	dep=de.estimate(img)
	dvis=depth.visualize_depth(dep)
	
	font=PIL.ImageFont.truetype("/usr/share/fonts/TTF/Hack-Bold.ttf",size=36)
	combined_vis=PIL.Image.new("RGB",img.size)
	draw=PIL.ImageDraw.Draw(combined_vis)
	for s in segs:
		
		#print("Segment shape",s.area.shape)
		#print(s.area)
		
		area_bool=~s.area.astype(bool)
		#print(area_bool)
		
		#print("Depth shape",dep.shape)
		#depth.visualize_depth(dep).save("out_dep_orig.jpg")
		
		dep_rsz=maths.resize_matrix(dep,s.area.shape)
		#print("Depth shape resized",dep_rsz.shape)
		#depth.visualize_depth(dep_rsz).save("out_dep_resz.jpg")
		
		# Masked array
		masked_depth=np.ma.MaskedArray(dep_rsz,mask=area_bool)
		#masked_depth=np.multiply(dep_rsz,s.area)
		#depth.visualize_depth(masked_depth).save("out_dep_masked.jpg")
		#print("Depth Mean:",masked_depth.mean())
		depth_mean=masked_depth.mean()
		
		
		print(F"{s.name} {s.confidence:.3f} {depth_mean:.1f}m")
		
		bbox_center_X=(s.xmin+s.xmax)/2
		bbox_center_Y=(s.ymin+s.ymax)/2
		shp=s.area.shape
		
		for i in range(len(s.points)):
			j=i-1
			startX=s.points[i][0]*img.width
			startY=s.points[i][1]*img.height
			endX=  s.points[j][0]*img.width
			endY=  s.points[j][1]*img.height
			#print(startX,startY,endX,endY)
			
			draw.line((startX,startY,endX,endY),fill="#FF0000",width=3)
		s=F"{s.name}\n{depth_mean:.1f}m"
		draw.text((bbox_center_X,bbox_center_Y),s,
			fill="#00FFFF",font=font,anchor="ms")
	
	if OUTPUT_MODE=="TK":
		tid_camraw.set_image(img)
		tid_hud_det.set_image(det_vis)
		tid_hud_seg.set_image(seg_vis)
		tid_depth.set_image(dvis)
		tid_combined.set_image(combined_vis)
	elif OUTPUT_MODE=="WEB":
		st.put_image("/raw.jpg",img)
		st.put_image("/det.jpg",det_vis)
		st.put_image("/seg.jpg",seg_vis)
		st.put_image("/dep.jpg",dvis)
		st.put_image("/com.jpg",combined_vis)
	elif OUTPUT_MODE=="FILE":
		img.save("out_raw.jpg")
		det_vis.save("out_det.jpg")
		seg_vis.save("out_seg.jpg")
		dvis.save("out_dep.jpg")
		combined_vis.save("out_com.jpg")
		
	
	


if IMAGE_SOURCE[0]=="WEBCAM":
	camera=cv2.VideoCapture(IMAGE_SOURCE[1])
	while True:
		res,img=camera.read()
		if not res:
			print("Cam read failed!")
			break

		pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

		display(pim)

elif IMAGE_SOURCE[0]=="IMGFILE":
	display(PIL.Image.open(IMAGE_SOURCE[1]))
elif IMAGE_SOURCE[0]=="VIDFILE":
	startT=time.time()
	while True:
		vt=time.time()-startT
		vf=video.get_video_frame(IMAGE_SOURCE[1],vt)
		if OUTPUT_MODE=="WEB":
			st.put_string("/information","{:.1f}s".format(vt))
		display(vf)
else:
	0/0

print("Main thread terminated.")
