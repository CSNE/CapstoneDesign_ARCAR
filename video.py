import subprocess
import io
import PIL.Image

def get_video_frame(vidpath,t):
	'''
	Grab video frame at time t (seconds)
	'''
	
	args=["ffmpeg"] # use FFMPEG
	args+=["-ss","{:.3f}s".format(t)] # Start time
	args+=["-i",vidpath] # Input file
	args+=["-frames:v","1"] # Grab 1 frame
	args+=["-c:v","mjpeg"] # output codec: JPEG
	args+=["-f","rawvideo"] # output muxer: raw
	args+=["-"] #output to stdout
	cp=subprocess.run(args,check=True,capture_output=True)
	
	virtual_file=io.BytesIO(cp.stdout)
	
	img= PIL.Image.open(virtual_file)
	img.load()
	return img
	
if __name__=="__main__":
	vf=get_video_frame("../KakaoTalk_20230310_155831877.mp4",1.53)
	vf.show()
	
