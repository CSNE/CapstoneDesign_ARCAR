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


def identify_image(pim,*,target_object):
	'''
	Identify & Display an image.
	pim is a PIL.Image object.
	returns two PIL.Image objects: detection bbox, and segmentation
	'''

	print("\n\n>>> GOT IMAGE",pim.size)

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
	det_out=PIL.Image.new("RGB",(ois[1],ois[0]))
	draw=PIL.ImageDraw.Draw(det_out)

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
		if ln==target_object:
			draw.rectangle(bo,outline="#FF0000",width=3)

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
	seg_out=None
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
		if ln==target_object:
			if seg_out is None:
				seg_out=aic
			else:
				seg_out=PIL.ImageChops.add(seg_out,aic)

	return (det_out,seg_out)
