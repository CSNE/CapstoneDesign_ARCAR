import ansi
import time

# Simple timer for crude performance measurement
class SequenceTimer:
	def __init__(self,*, 
			prefix="",
			text_length=30, ms_format="5.0",
			orange_thresh=0.2, red_thresh=1.0,
			print_in_progress=True):
		self._tl=text_length
		self._ot=orange_thresh
		self._rt=red_thresh
		
		self._pip=print_in_progress
		self._pf=prefix
		namelen=self._tl-len(self._pf)
		self._fmtstr_name=("{:<"+str(namelen)+"s}")
		self._fmtstr_ms=("{:>"+ms_format+"f}")
		self._ms_len=len(self._fmtstr_ms.format(0.0))+2
		
		self._current_segment_name=None
		self._current_segment_start=None
	
	def _print(self,name,delta=None):
		print(ansi.MAGENTA+self._pf+" ",end='')
		print(ansi.BOLD+self._fmtstr_name.format(name)+ansi.RESET,end='')
		
		if delta is None:
			# Segment start - don't go to newline yet
			pass#print(ansi.WHITE+ansi.BLINK+" "*((self._ms_len-3)//2)+"..."+ansi.RESET+"\r",flush=True,end='')
			print("\r",flush=True,end='')
			
		else:
			if delta<self._ot:
				clr=ansi.GREEN
			elif delta<self._rt:
				clr=ansi.YELLOW
			else:
				clr=ansi.RED
			
			print(clr+self._fmtstr_ms.format(delta*1000)+"ms"+ansi.RESET)
		
		
	def start_segment(self,name=None,*,t=None):
		if t is None:
			t=time.time()
		
		self._current_segment_start=t
		
		self._current_segment_name=None
		if name is not None:
			self._current_segment_name=name
			if self._pip:
				self._print(name)
		
	def end_segment(self,name=None,*,t=None):
		if t is None:
			t=time.time()
		
		if name is not None:
			self._current_segment_name=name
			
		if self._current_segment_name is None:
			return
		if self._current_segment_start is None:
			return
		
		name=self._current_segment_name
		delta=t-self._current_segment_start
		
		self._print(name,delta)
		
		self._current_segment_name=None
		self._current_segment_start=None
		
	def split(self,*,starting=None,ending=None):
		t=time.time()
		self.end_segment(ending,t=t)
		self.start_segment(starting,t=t)
		
if __name__=="__main__":
	st1=SequenceTimer()
	st2=SequenceTimer()
	st1.split(starting="Whole")
	st2.split(starting="Section 1")
	time.sleep(0.1) # Section 1
	st2.split(starting="Section 2")
	time.sleep(0.2) # Section 2
	st2.split(starting="Section 3")
	time.sleep(0.3) # Section 3
	st2.split(starting="Section 4")
	time.sleep(0.4) # Section 4
	st2.split()
	time.sleep(0.5) # Section 5 -  If a section is never named, it is not printed
	st2.split()
	time.sleep(0.6) # Section 6
	st2.split(ending="Section 6") # We can also name the segment at the end
	st1.split()
