# Some helper classes, for displaying an image with tkinter.


import PIL.ImageTk
import tkinter
import threading

class ImageDisplayerRoot(threading.Thread):
	'''
	A tkinter root instance running on its own thread.
	For usage with ImageDisplayWindow.
	'''
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self._alive=True
	def is_alive(self):
		return self._alive
	def die(self):
		if not self._alive:
			return #don't die twice'
		self._alive=False
		self.run_in_tk_thread(lambda:self._tkroot.destroy())
	def run_in_tk_thread(self,func):
		self._tkroot.after(0,func)
	@property
	def opt_mirror(self):
		if hasattr(self,"_mirror_var"):
			return self._mirror_var.get()!=0
		else:
			print("NOATTR!")
			return False
	@property
	def rootwindow(self):
		return self._tkroot
	def run(self):
		print("tk thread started.")
		self._tkroot=tkinter.Tk()
		self._kill_btn=tkinter.Button(self._tkroot,
								text="Die",
								command=self.die)
		self._kill_btn.pack()
		self._mirror_var=tkinter.IntVar()
		self._mirror_cb=tkinter.Checkbutton(self._tkroot,
								text="Mirror?",
								variable=self._mirror_var)
		self._mirror_cb.pack()
		self._tkroot.mainloop()
		print("tk thread terminated.")

class ImageDisplayWindow:
	'''
	A tkinter window that displays an image.
	'''
	def __init__(self,idr,title):
		self._idr=idr
		self._idr.run_in_tk_thread(self._initialize)
		self._title=title

	def _image_setter(self,img):
		w=self._tl.winfo_width()
		h=self._tl.winfo_height()
		w=max(w-4,320)
		h=max(h-4,180)
		img=img.resize((w,h))
		ti=PIL.ImageTk.PhotoImage(img)
		self._ti_cache=ti
		self._trl.configure(image=ti)

	def set_image(self,pil_image):
		self._idr.run_in_tk_thread(lambda: self._image_setter(pil_image))

	def _initialize(self):
		self._tl=tkinter.Toplevel(self._idr.rootwindow)
		self._tl.title(self._title)
		self._trl=tkinter.Label(self._tl)
		self._trl.grid(row=1,column=1,sticky=(tkinter.W,tkinter.E,tkinter.N,tkinter.S))
		self._tl.columnconfigure(1,weight=1)
		self._tl.rowconfigure(1,weight=1)
