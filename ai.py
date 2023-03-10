# 3rd-Party
import ultralytics
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageChops
import numpy

# std library
import random

## Model Setup
#model = YOLO("yolov8n.pt")
model_det = ultralytics.YOLO("yolov8s.pt")
model_seg = ultralytics.YOLO("yolov8s-seg.pt")
#model = YOLO("yolov8s-cls.pt")


def detect(pim,*,target_object):
	print("\n>>> DETECT...")

	# Run model
	results_det=model_det(pim)
	assert len(results_det)==1
	result_det=results_det[0]

	# Results
	orig_size=result_det.orig_shape
	boxes=(result_det.boxes.xyxyn).tolist()
	confidences=(result_det.boxes.conf).tolist()
	classes=(result_det.boxes.cls).tolist()

	# Prepare to draw
	det_out=PIL.Image.new("RGB",(orig_size[1],orig_size[0]))
	draw=PIL.ImageDraw.Draw(det_out)

	# Draw the bounding boxes
	print("DETECTION BBOXES")
	for i in range(len(boxes)):
		b=boxes[i] # This is in relative coordinates
		c=confidences[i]
		n=result_det.names[classes[i]]

		# Convert to actual coordinates
		bo=[b[0]*orig_size[1], #Xmin
			b[1]*orig_size[0], #Ymin
			b[2]*orig_size[1], #Xmax
			b[3]*orig_size[0]] #Ymax

		print(F"X{bo[0]:.0f}-{bo[2]:.0f}/{orig_size[1]} Y{bo[1]:.0f}-{bo[3]:.0f}/{orig_size[0]} C{c:.3f} {n}")
		if n==target_object:
			draw.rectangle(bo,outline="#FF0000",width=3)
	return det_out

def segment(pim,*,target_object):
	# Run model
	print("\n\n>>> SEGMENT...")
	results_seg=model_seg(pim)
	assert len(results_seg)==1
	result_seg=results_seg[0]

	# Get results
	orig_size=result_seg.orig_shape
	masks=result_seg.masks
	segs=masks.segments
	areas=masks.data
	confidences=(result_seg.boxes.conf).tolist()
	classes=(result_seg.boxes.cls).tolist()

	# Draw all masks on image
	print("MASKS")
	seg_out=None
	for i in range(len(masks)):
		# Mask data
		m=masks[i]
		c=confidences[i]
		n=result_seg.names[classes[i]]
		a=areas[i]

		# Convert mask to PIL Image
		npa=a.numpy()
		ai=PIL.Image.fromarray(
			numpy.uint8(npa*255)
			).convert("L")

		# Randomly colorize area
		randcom_color=[random.randint(100,255) for i in range(3)]
		aic=PIL.ImageOps.colorize(ai,(0,0,0),randcom_color)

		print(c,n,len(a),len(a[0]))

		# Composite onto the result image
		if n==target_object:
			if seg_out is None:
				seg_out=aic
			else:
				seg_out=PIL.ImageChops.add(seg_out,aic)

	return seg_out
