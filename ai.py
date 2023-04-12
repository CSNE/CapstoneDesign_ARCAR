# YOLO-related functions.

# 3rd-Party
import ultralytics
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageChops
import numpy

# std library
import random
import collections

## Model Setup
#model = YOLO("yolov8n.pt")
model_det = ultralytics.YOLO("yolov8s.pt")
model_seg = ultralytics.YOLO("yolov8s-seg.pt")
#model = YOLO("yolov8s-cls.pt")

# namedtuple for storing the detection results.
DetectionResult=collections.namedtuple(
	"DetectionResult",
	["xmin","xmax","ymin","ymax","confidence","name"])

def detect(pim):
	'''
	Run detection on YOLO, given a PIL image.
	'''
	# Run model
	results_det=model_det(pim)
	assert len(results_det)==1
	result_det=results_det[0]

	# Results
	orig_size=result_det.orig_shape
	boxes=(result_det.boxes.xyxyn).tolist()
	confidences=(result_det.boxes.conf).tolist()
	classes=(result_det.boxes.cls).tolist()

	# collect results
	results=[]
	for i in range(len(boxes)):
		b=boxes[i] # This is in relative coordinates
		c=confidences[i]
		n=result_det.names[classes[i]]

		results.append(
			DetectionResult(
				xmin=b[0]*orig_size[1],
				xmax=b[2]*orig_size[1],
				ymin=b[1]*orig_size[0],
				ymax=b[3]*orig_size[0],
				confidence=c,
				name=n))
	return results

def visualize_detections(detections,size):
	'''
	Visualze detection results.
	'''
	# Prepare to draw
	det_out=PIL.Image.new("RGB",size)
	draw=PIL.ImageDraw.Draw(det_out)

	# Draw the bounding boxes
	for d in detections:
		# Convert to actual coordinates
		bo=[d.xmin,d.ymin,d.xmax,d.ymax]
		draw.rectangle(bo,outline="#FF0000",width=3)
	return det_out

# namedtuple for storing the segmentation results.
SegmentationResult=collections.namedtuple(
	"SegmentationResult",
	["points","area","confidence","name","xmin","xmax","ymin","ymax"])

def segment(pim):
	'''
	Run segmentation on YOLO, given a PIL image.
	'''
	
	# Run model
	results_seg=model_seg(pim)
	assert len(results_seg)==1
	result_seg=results_seg[0]

	# Get results
	orig_size=result_seg.orig_shape
	masks=result_seg.masks
	if masks is None: # No detections
		return []
	segs=masks.xyn
	areas=masks.data
	boxes=(result_seg.boxes.xyxyn).tolist()
	confidences=(result_seg.boxes.conf).tolist()
	classes=(result_seg.boxes.cls).tolist()
	
	# collect results
	results=[]
	for i in range(len(masks)):
		# Mask data
		m=masks[i]
		c=confidences[i]
		n=result_seg.names[classes[i]]
		b=boxes[i]
		a=areas[i]
		npa=a.numpy()
		s=segs[i]
		
		results.append(
			SegmentationResult(
				points=s,
				area=npa,
				confidence=c,
				name=n,
				xmin=b[0]*orig_size[1],
				xmax=b[2]*orig_size[1],
				ymin=b[1]*orig_size[0],
				ymax=b[3]*orig_size[0]))
	return results

def visualize_segmentation(segments,size):
	'''
	Visualze segmentation results.
	'''
	# Draw all masks on image
	seg_out=PIL.Image.new("RGB",size)
	for s in segments:
		ai=PIL.Image.fromarray(numpy.uint8(s.area*255)).convert("L")
		
		# Randomly colorize area
		randcom_color=[random.randint(100,255) for i in range(3)]
		aic=PIL.ImageOps.colorize(ai,(0,0,0),randcom_color)

		# Composite onto the result image
		seg_out=PIL.ImageChops.add(seg_out,aic)

	return seg_out
