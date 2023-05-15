import webcam
import sys
import PIL.ImageChops
import tk_display
import time

idL=int(sys.argv[1])
idR=int(sys.argv[2])
print(F"Cam ID: L {idL} / R {idR}")

img_disp_root=tk_display.ImageDisplayerRoot()
img_disp_root.start()
camL=webcam.ThreadedWebcam(idL)
camL.start()
camR=webcam.ThreadedWebcam(idR)
camR.start()
time.sleep(2) # Race condition

tidL=tk_display.ImageDisplayWindow(img_disp_root,"Left")
tidR=tk_display.ImageDisplayWindow(img_disp_root,"Right")
tidD=tk_display.ImageDisplayWindow(img_disp_root,"Diff")



try:
	while img_disp_root.is_alive():

		pimL=camL.grab()
		pimR=camR.grab()

		pimD=PIL.ImageChops.difference(pimL,pimR)

		tidL.set_image(pimL)
		tidR.set_image(pimR)
		tidD.set_image(pimD)
except KeyboardInterrupt:
	pass
finally:
	print("Killing threads...")
	img_disp_root.die()
	camL.die()
	camR.die()
