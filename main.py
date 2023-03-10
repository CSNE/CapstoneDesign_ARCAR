# Options

#IMAGE_SOURCE=("WEBCAM",3) #Webcam index
IMAGE_SOURCE=("IMGFILE","vlcsnap-2023-03-10-22h57m59s043.png") #Image file and path

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
# matplotlib
# numpy
# tkinter (from Python standard library)

# Probably won't run in a virtual enviornment, due to it requiring tkinter.

# Standard Library
import time
import random

# 3rd-Party
import ultralytics
import PIL.Image
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageChops
import cv2
import matplotlib.cm
import numpy

# Local modules
import gui


## GUI Setup
img_disp_root=gui.ImageDisplayerRoot()
img_disp_root.start()
time.sleep(0.5) # Race condition

tid_hud_det=gui.ImageDisplayWindow(img_disp_root,"Detection")
tid_hud_seg=gui.ImageDisplayWindow(img_disp_root,"Segmentation")
tid_camraw=gui.ImageDisplayWindow(img_disp_root,"Source Image")


## Model Setup
#model = YOLO("yolov8n.pt")
model_det = ultralytics.YOLO("yolov8s.pt")
model_seg = ultralytics.YOLO("yolov8s-seg.pt")
#model = YOLO("yolov8s-cls.pt")

def identify_image(pim):
	'''
	Identify & Display an image.
	pim is a PIL.Image object.
	'''

	print("\n\n>>> GOT IMAGE",pim.size)
	tid_camraw.set_image(pim)


	print("\n>>> DETECT...")
	results_det=model_det(pim)
	assert len(results_det)==1
	result_det=results_det[0]


	#print("RESULT:",type(r))
	#print(r)
	#r=r.cpu()
	#print("names",r.names)
	#print("boxes",r.boxes)
	ois=result_det.orig_shape
	#print(ois)
	boxes=(result_det.boxes.xyxyn).tolist()
	confidences=(result_det.boxes.conf).tolist()
	classes=(result_det.boxes.cls).tolist()

	#drawn=pim.copy()
	drawn=PIL.Image.new("RGB",(ois[1],ois[0]))
	draw=PIL.ImageDraw.Draw(drawn)

	print("DETECTION BBOXES")
	for i in range(len(boxes)):
		b=boxes[i]
		c=confidences[i]
		l=classes[i]
		ln=result_det.names[l]
		#print(result_det.names)
		#print(b,c,l,ln)
		bo=[
			b[0]*ois[1], #Xmin
			b[1]*ois[0], #Ymin
			b[2]*ois[1], #Xmax
			b[3]*ois[0]] #Ymax
		print(F"X{bo[0]:.0f}-{bo[2]:.0f}/{ois[1]} Y{bo[1]:.0f}-{bo[3]:.0f}/{ois[0]} C{c:.3f} {ln}")
		if ln==TARGET_OBJECT:
			draw.rectangle(bo,outline="#FF0000",width=3)

	tid_hud_det.set_image(drawn)


	print("\n\n>>> SEGMENT...")
	results_seg=model_seg(pim)
	assert len(results_seg)==1
	result_seg=results_seg[0]

	ois=result_seg.orig_shape
	#print(ois)
	masks=result_seg.masks
	segs=masks.segments
	#print("S",segs)
	areas=masks.data
	#print("A",areas)
	confidences=(result_seg.boxes.conf).tolist()
	classes=(result_seg.boxes.cls).tolist()

	print("MASKS")
	out_img=None
	for i in range(len(masks)):
		m=masks[i]
		c=confidences[i]
		l=classes[i]
		ln=result_seg.names[l]
		a=areas[i]
		npa=a.numpy()
		ai=PIL.Image.fromarray(
			numpy.uint8(npa*255)
			).convert("L")
		randcom_color=[random.randint(100,255) for i in range(3)]
		aic=PIL.ImageOps.colorize(ai,(0,0,0),randcom_color)
		'''
		if img_disp_root.opt_mirror:
			ai=ai.transpose(PIL.Image.FLIP_LEFT_RIGHT)
		'''
		print(c,ln,len(a),len(a[0]))
		# This just overwrites, should do some compositing or sth
		if ln==TARGET_OBJECT:
			if out_img is None:
				out_img=aic
			else:
				out_img=PIL.ImageChops.add(out_img,aic)
	if out_img is not None:
		tid_hud_seg.set_image(out_img)


if IMAGE_SOURCE[0]=="WEBCAM":
	camera=cv2.VideoCapture(IMAGE_SOURCE[1])
	while img_disp_root.is_alive():
		res,img=camera.read()
		if not res:
			print("Cam read failed!")
			break

		pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
		#print(pim)
		if img_disp_root.opt_mirror:
			pim=pim.transpose(PIL.Image.FLIP_LEFT_RIGHT)

		identify_image(pim)

elif IMAGE_SOURCE[0]=="IMGFILE":
	identify_image(PIL.Image.open(IMAGE_SOURCE[1]))
elif IMAGE_SOURCE[0]=="VIDFILE":
	#TODO implement video reading
	pass
else:
	0/0

print("Terminated.")
