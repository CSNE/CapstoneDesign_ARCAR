import cv2
import time
import PIL.Image
import numpy

import tk_display
import visualizations
import webcam

def pil2cv(pimg):
	return cv2.cvtColor(numpy.array(pimg.convert("RGB")), cv2.COLOR_RGB2BGR)
def stereo_calculate(*,left,right,depth_multiplier=1.0):
	stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)
	disparity = stereo.compute(
		cv2.cvtColor(pil2cv(left), cv2.COLOR_BGR2GRAY),
		cv2.cvtColor(pil2cv(right), cv2.COLOR_BGR2GRAY))
	disparity_masked=numpy.ma.masked_less_equal(disparity,0)
	disparity_float=disparity_masked.astype(float)
	depth=1/disparity_float
	return depth*depth_multiplier

def demo_realtime():
	img_disp_root=tk_display.ImageDisplayerRoot()
	img_disp_root.start()
	time.sleep(0.5) # Race condition

	tid_cL=tk_display.ImageDisplayWindow(img_disp_root,"Camera L")
	tid_cR=tk_display.ImageDisplayWindow(img_disp_root,"Camera R")
	tid_d=tk_display.ImageDisplayWindow(img_disp_root,"Depth")

	camL=webcam.Webcam(4)
	camR=webcam.Webcam(2)

	while True:

		pimL=camL.grab()
		pimR=camR.grab()

		disparity=stereo_calculate(left=pimL,right=pimR)
		vis=visualizations.visualize_matrix(disparity)

		tid_cL.set_image(pimL)
		tid_cR.set_image(pimR)
		tid_d.set_image(vis)

def demo_img():
	imgL=PIL.Image.open("tsukuba_l.png")
	imgR=PIL.Image.open("tsukuba_r.png")
	disparity=stereo_calculate(left=imgL,right=imgR)
	vis=visualizations.visualize_matrix(disparity)
	vis.save("disparity.png")
if __name__=="__main__":
	#demo_img()
	demo_realtime()
