import webcam
import sys
import time
import subprocess
import os.path

idL=int(sys.argv[1])
idR=int(sys.argv[2])
savename=sys.argv[3]
print(F"Cam ID: L {idL} / R {idR}")
savepathL="captures/"+savename+"_L.jpg"
savepathR="captures/"+savename+"_R.jpg"

if os.path.exists(savepathL) or os.path.exists(savepathR):
	print("File exists already overwrite?")
	input("Enter to overwrite.")

camL=webcam.ThreadedWebcam(idL)
camL.start()
camR=webcam.ThreadedWebcam(idR)
camR.start()
for i in (3,2,1):
	print("Capture in...",i)
	time.sleep(1) # Race condition



#savename=str(round(time.time()))



pimL=camL.grab().save(savepathL)
pimR=camR.grab().save(savepathR)



camL.die()
camR.die()

subprocess.run(["gwenview",savepathL])
