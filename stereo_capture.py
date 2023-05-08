import webcam
import sys
import time

idL=int(sys.argv[1])
idR=int(sys.argv[2])
savename=sys.argv[3]
print(F"Cam ID: L {idL} / R {idR}")


camL=webcam.ThreadedWebcam(idL)
camL.start()
camR=webcam.ThreadedWebcam(idR)
camR.start()
for i in (4,3,2,1):
	print("Capture in...",i)
	time.sleep(1) # Race condition



#savename=str(round(time.time()))

pimL=camL.grab().save("captures/"+savename+"_L.jpg")
pimR=camR.grab().save("captures/"+savename+"_R.jpg")



camL.die()
camR.die()
