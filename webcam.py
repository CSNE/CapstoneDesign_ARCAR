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

import threading
class ThreadedWebcam(threading.Thread):
    def __init__(self,n,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._alive=True
        #self._cv_img=None
        self._pil_img=None
        self._vc=cv2.VideoCapture(n)
        self._n=n
    def run(self):
        while self._alive:
            res,img=self._vc.read()
            if not res:
                raise WebcamError("Cam read (id:{}) failed!".format(self._n))
            self._pil_img=PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    def grab(self):
        return self._pil_img
    def die(self):
        self._alive=False
