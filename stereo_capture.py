import webcam
import sys
import time
import subprocess
import os.path

idL=int(sys.argv[1])
idR=int(sys.argv[2])
mode=sys.argv[3].lower()
savename=sys.argv[4]

assert mode in ("p","v") # Photo or Video

print(F"Cam ID: L {idL} / R {idR}")
if mode=="p":
	print("PHOTO (Single-Frame)")
else:
	print("VIDEO (Multi-Frame)")


savepathL="captures/"+savename+"_L.jpg"
savepathR="captures/"+savename+"_R.jpg"
savepathV="captures/"+savename

if os.path.exists(savepathL) or os.path.exists(savepathR) or os.path.exists(savepathV):
		print("File exists already.")
		sys.exit(1)

if mode=="v":
	os.mkdir(savepathV)

camL=webcam.ThreadedWebcam(idL)
camL.start()
camR=webcam.ThreadedWebcam(idR)
camR.start()

for i in (3,2,1):
	print("Capture in...",i)
	time.sleep(1) # Race condition


#savename=str(round(time.time()))

if mode=="p":
	pimL=camL.grab().save(savepathL)
	pimR=camR.grab().save(savepathR)
else:
	frmN=0
	lastFrmT=-1000
	capStartT=time.time()
	try:
		while True:
			while True:
				t=time.time()-capStartT
				if t>lastFrmT+0.2: #5fps
					break
				time.sleep(0.01)
			pimL=camL.grab()
			pimR=camR.grab()

			fp=os.path.join(savepathV,"{:05d}_{:08d}".format(frmN,round(t*1000)))
			print("\r"+fp,flush=True,end='')
			fnL=fp+"_L.jpg"
			fnR=fp+"_R.jpg"

			pimL.save(fnL)
			pimR.save(fnR)

			frmN+=1
			lastFrmT=t

	except KeyboardInterrupt:
		print("Stop capture.")

camL.die()
camR.die()
