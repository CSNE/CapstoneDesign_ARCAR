# Options

#IMAGE_SOURCE=("WEBCAM",2) #Webcam index
#IMAGE_SOURCE=("IMGFILE","testimg.png") #Image file and path
IMAGE_SOURCE=("VIDFILE","../KakaoTalk_20230310_155831877.mp4") #Video file and path

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

# 3rd party
import PIL.Image
import cv2

# Local modules
import gui
import ai
import depth
import video

## GUI Setup
img_disp_root=gui.ImageDisplayerRoot()
img_disp_root.start()
time.sleep(0.5) # Race condition

tid_hud_det=gui.ImageDisplayWindow(img_disp_root,"Detection")
tid_hud_seg=gui.ImageDisplayWindow(img_disp_root,"Segmentation")
tid_camraw=gui.ImageDisplayWindow(img_disp_root,"Source Image")
tid_depth=gui.ImageDisplayWindow(img_disp_root,"Depth Estimation")

de=depth.DepthEstimator()

def display(img):
	if img_disp_root.opt_mirror:
		img=img.transpose(PIL.Image.FLIP_LEFT_RIGHT)

		
	tid_camraw.set_image(img)

	det=ai.detect(img,target_object=TARGET_OBJECT)
	tid_hud_det.set_image(det)

	seg=ai.segment(img,target_object=TARGET_OBJECT)
	if seg is not None:
		tid_hud_seg.set_image(seg)

	dep=de.estimate(img)
	dvis=depth.visualize_depth(dep)
	tid_depth.set_image(dvis)


if IMAGE_SOURCE[0]=="WEBCAM":
	camera=cv2.VideoCapture(IMAGE_SOURCE[1])
	while img_disp_root.is_alive():
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
		vf=video.get_video_frame(IMAGE_SOURCE[1],time.time()-startT)
		display(vf)
else:
	0/0

print("Main thread terminated.")
