# YOLO-related functions.

# 3rd-Party
import ultralytics
import PIL.Image

# std library
import collections

## Model Setup
model_seg = ultralytics.YOLO("yolov8s-seg.pt")


# namedtuple for storing the segmentation results.
SegmentationResult=collections.namedtuple(
	"SegmentationResult",
	["points","area","confidence","name","xmin","xmax","ymin","ymax"])

def segment(pim:PIL.Image) -> SegmentationResult:
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


