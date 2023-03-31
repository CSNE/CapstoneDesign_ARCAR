# Options

#IMAGE_SOURCE=("WEBCAM",2) #Webcam index
#IMAGE_SOURCE=("IMGFILE","testimg.png") #Image file and path
IMAGE_SOURCE=("VIDFILE","../KakaoTalk_20230310_155831877.mp4") #Video file and path

#OUTPUT_MODE="TK"
OUTPUT_MODE="WEB"

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

# Local modules
import gui
import ai
import depth
import video
import web

## GUI Setup
if OUTPUT_MODE=="TK":
	img_disp_root=gui.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	tid_hud_det=gui.ImageDisplayWindow(img_disp_root,"Detection")
	tid_hud_seg=gui.ImageDisplayWindow(img_disp_root,"Segmentation")
	tid_camraw=gui.ImageDisplayWindow(img_disp_root,"Source Image")
	tid_depth=gui.ImageDisplayWindow(img_disp_root,"Depth Estimation")

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
			
	
	if OUTPUT_MODE=="TK":
		tid_camraw.set_image(img)
	elif OUTPUT_MODE=="WEB":
		st.put_image("/raw.jpg",img)

	det=ai.detect(img,target_object=TARGET_OBJECT)
	if OUTPUT_MODE=="TK":
		tid_hud_det.set_image(det)
	elif OUTPUT_MODE=="WEB":
		st.put_image("/det.jpg",det)

	seg=ai.segment(img,target_object=TARGET_OBJECT)
	if seg is not None:
		if OUTPUT_MODE=="TK":
			tid_hud_seg.set_image(seg)
		elif OUTPUT_MODE=="WEB":
			st.put_image("/seg.jpg",seg)

	dep=de.estimate(img)
	dvis=depth.visualize_depth(dep)
	if OUTPUT_MODE=="TK":
		tid_depth.set_image(dvis)
	elif OUTPUT_MODE=="WEB":
		st.put_image("/dep.jpg",dvis)
	
	


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
