import cv2
import PIL.Image

class WebcamError(BaseException):
    pass

class Webcam:
    def __init__(self,n):
        self._vc=cv2.VideoCapture(n)
        self._n=n
    def grab(self):
        res,img=self._vc.read()
        if not res:
            raise WebcamError("Cam read (id:{}) failed!".format(self._n))
        pim=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return pim
