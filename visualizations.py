# Visualization-related functions

import PIL.Image
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageChops

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
# Workaround for Matplotlib erroring on Qt error
mpl.use('Agg')

import numpy
import numpy.ma
import random
import io

import yolodriver

def visualize_segmentations(segments: list[yolodriver.SegmentationResult],size):
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

def visualize_matrix(arr,title=None,target_aspect=(9/16),clip_percentiles=None):
	'''
	Visualize a numpy 2D array to a PIL image, using matplotlib
	'''
	if clip_percentiles:
		assert len(clip_percentiles)==2 #min,max
		assert clip_percentiles[0]<clip_percentiles[1]
		naned = numpy.ma.filled(arr, numpy.nan)
		pv=numpy.nanpercentile(naned,clip_percentiles)
		arr=numpy.clip(arr,pv[0],pv[1])
		
	array_aspect=arr.shape[0]/arr.shape[1]

	fig = plt.figure()
	cmap=mpl.colormaps.get_cmap("plasma").reversed()
	ax = fig.add_subplot()
	ax.set_facecolor("#00A000")
	if title is not None:
		ax.set_title(title)
	plt.imshow(arr,cmap=cmap)
	ax.set_aspect(target_aspect/array_aspect) #height=N*width
	plt.colorbar(orientation='vertical')

	bio=io.BytesIO()
	plt.savefig(bio)
	bio.seek(0)
	plt.close(fig)
	return PIL.Image.open(bio).convert("RGB")

# Load Font
font_list=[
	"/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", # Ubuntu
	"/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono-Bold.ttf", # Fedora 37
	"/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf", # Archlinux
	"arialbd.ttf", # Windows
	"arial.ttf" # Windows 2
	]
font_size=36
font=None
for font_path in font_list:
	try:
		font=PIL.ImageFont.truetype(font_path,size=36)
		print("Font",font_path.split("/")[-1],"loaded")
		break
	except OSError:
		pass
if font is None:
	print("Font load failed - loading default font")
	font=PIL.ImageFont.load_default()


def visualize_segdepth(segdepths,size,bg=None):
	'''
	Visualize segdepths.
	'''
	if bg is None:
		vis=PIL.Image.new("RGB",size)
	else:
		vis=bg.copy()
	draw=PIL.ImageDraw.Draw(vis)

	for sd in segdepths:

		dep=sd.depth_average
		dep_percentage=sd.depth_valid_ratio*100
		seg=sd.segment

		bbox_center_X=(seg.xmin+seg.xmax)/2
		bbox_center_Y=(seg.ymin+seg.ymax)/2

		# Draw outline
		for i in range(len(seg.points)):
			j=i-1
			startX=seg.points[i][0]*size[0]
			startY=seg.points[i][1]*size[1]
			endX=  seg.points[j][0]*size[0]
			endY=  seg.points[j][1]*size[1]
			draw.line((startX,startY,endX,endY),fill="#FF0000",width=3)

		# Write text
		draw.text(
			(bbox_center_X,bbox_center_Y),
			F"{seg.name}\n{dep:.1f}m\n{dep_percentage:.1f}%",
			fill="#00FFFF",font=font,anchor="ms")
	return vis

import random
import maths
def compare_depthmaps(*,ai,ir,sample=100):
	# Get all valid IR coords
	sample_points=maths.sample_npa(ir)

	# Resize AI to IR
	ai_resized=maths.resize_matrix(ai,ir.shape)

	xdata=[]
	ydata=[]
	for y,x in sample_points:
		#print("Coords:",x,y)
		point_ai=ai_resized[y][x]
		point_ir=ir[y][x]
		#print("AI",point_ai,"IR",point_ir)
		xdata.append(point_ai)
		ydata.append(point_ir)
	return scatter(x=xdata,y=ydata,xlabel="AI Depth",ylabel="IR Depth")


def scatter(*,x,y,xlabel=None,ylabel=None):
	fig = plt.figure()
	plt.scatter(x,y)
	if xlabel is not None:
		plt.xlabel(xlabel)
	if ylabel is not None:
		plt.ylabel(ylabel)

	bio=io.BytesIO()
	plt.savefig(bio)
	bio.seek(0)
	plt.close(fig)
	return PIL.Image.open(bio).convert("RGB")

if __name__=="__main__":
	scatter([1,2],[1,2]).show()
