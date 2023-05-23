
import os
import os.path
import collections
import PIL.Image
import time
import random

Frame = collections.namedtuple(
    "Frame",
    ["frame_number","ms","left","right"])
class StereoPlayback:
    def __init__(self,dirpath):
        self._dp=dirpath
        files=os.listdir(dirpath)

        files.sort()
        self._frames=[]
        for fn in files:
            if not fn.endswith("_L.jpg"):
                continue
            fnL=fn
            fnR=fn.replace("_L.jpg","_R.jpg")
            fns=fn.split("_")
            fnum=int(fns[0])
            ms=int(fns[1])
            self._frames.append(
                Frame(
                    frame_number=fnum,
                    ms=ms,
                    left=os.path.join(dirpath,fnL),
                    right=os.path.join(dirpath,fnR)))
        self._fidx=0
        
        self._is_playing=False
        self._play_start_vidtime=0
        self._play_start_walltime=0
    
    def reanchor_play(self):
        self._play_start_vidtime=self._frames[self._fidx].ms
        self._play_start_walltime=time.time()
    def play(self):
        self.reanchor_play()
        self._is_playing=True
    def stop(self):
        self._is_playing=False
    
    def update(self):
        if self._is_playing:
            dT=time.time()-self._play_start_walltime
            self.set_time(dT*1000+self._play_start_vidtime)
    def set_time(self,ms):
        #print("time set",ms)
        while (self._fidx+1)<len(self._frames):
            if ms<self._frames[self._fidx+1].ms:
                break
            self._fidx+=1
            #print(self._fidx)
    def set_frame(self,n):
        self._fidx=n
        self.constrain_frame_index()
        self.reanchor_play()
    
    def randframe(self):
        self._fidx=random.randint(0,len(self._frames)-1)
    def delta_frame(self,d):
        self._fidx+=d
        self.constrain_frame_index()
        self.reanchor_play()
    def rewind(self):
        self._fidx=0
        self.reanchor_play()
    def constrain_frame_index(self):
        if self._fidx<0:
            self._fidx=0
        if self._fidx >= len(self._frames):
            self._fidx= (len(self._frames)-1)
            
    @property
    def frameindex(self):
        return self._fidx
        
    def over(self):
        return self._fidx == len(self._frames)-1
    def get_frame_fp(self):
        fpL=self._frames[self._fidx].left
        fpR=self._frames[self._fidx].right
        return fpL,fpR
    def get_frame(self):
        fpL,fpR=self.get_frame_fp()
        return (PIL.Image.open(fpL),PIL.Image.open(fpR))


