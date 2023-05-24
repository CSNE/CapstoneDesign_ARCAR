# YOLO-related functions.

# 3rd-Party
import ultralytics
import PIL.Image

# std library
import collections

# Local
import coordinates
import magic

## Model Setup
model_seg_official= ultralytics.YOLO("yolov8s-seg-official.pt")
model_seg_custom = ultralytics.YOLO("yolov8s-seg-custom.pt")

# namedtuple for storing the segmentation results.
SegmentationResult=collections.namedtuple(
	"SegmentationResult",
	["points_ratio","points_pixel",
	 "area","confidence","name",
	 "bbox_ratio","bbox_pixel"])


def segment(pim:PIL.Image,use_cuda=False):
	res=[]
	if magic.yolo.run_official_pretrained_model:
		res.extend(segment_(pim,model_seg_official,use_cuda))
	res.extend(segment_(pim,model_seg_custom,use_cuda))
	return res
	
def segment_(pim:PIL.Image,model,use_cuda=False):
	'''
	Run segmentation on YOLO, given a PIL image.
	'''

	# Run model
	dev="cpu"
	if use_cuda:
		dev="0" #CUDA device 0
	results_seg=model(pim,device=dev)
	assert len(results_seg)==1
	result_seg=results_seg[0]

	# Get results
	
	orig_sizeX=result_seg.orig_shape[1]
	orig_sizeY=result_seg.orig_shape[0]
	assert (orig_sizeX,orig_sizeY) == pim.size
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
		npa=a.cpu().numpy()
		#print("Seg len",segs[i].shape)
		s=segs[i]
		#print(s)
		s_px=[]
		s_rel=[]
		for coords in s:
			# Cast to regular python floats from np.float64 because why not
			s_px.append(
				coordinates.Coordinates2D(
					x=float(coords[0]*orig_sizeX),
					y=float(coords[1]*orig_sizeY)))
			s_rel.append(
				coordinates.Coordinates2D(
					x=float(coords[0]),
					y=float(coords[1])))
		
		bbx_rat=coordinates.BoundingBox(
			xmin=float(b[0]),
			xmax=float(b[2]),
			ymin=float(b[1]),
			ymax=float(b[3]))
		bbx_px=coordinates.BoundingBox(
			xmin=float(b[0]*orig_sizeX),
			xmax=float(b[2]*orig_sizeX),
			ymin=float(b[1]*orig_sizeY),
			ymax=float(b[3]*orig_sizeY))

		results.append(
			SegmentationResult(
				points_ratio=s_rel,
				points_pixel=s_px,
				area=npa,
				confidence=c,
				name=n,
				bbox_ratio=bbx_rat,
				bbox_pixel=bbx_px))
	return results


