# Webserver-related code

import http.server
import threading
import time
import io
import json

import PIL.Image

class ServerThread(threading.Thread):
	'''
	A programmable server on its own thread. Start with:
	st=ServerThread(PORT)
	st.start()
	
	Insert data with
	st.put_data("/test",b"asdf",mimetype="text/plain")
	st.put_image("/img.png",pil_image)
	etc
	
	now server will reply with "asdf" whenever you access localhost:PORT/test
	'''
	def __init__(self,port):
		super().__init__()
		self._port=port
		self._serve_data=dict()
		self._mimetypes=dict()
		
		outer_self=self
		class ReqHandler(http.server.BaseHTTPRequestHandler):
			def log_message(self, format, *args): #supress log messages
				return
			def do_GET(self):
				path=self.path.split("?")[0]
				client_addr, client_port=self.client_address
				
				try:
					response=outer_self._get_data(path)
					self.send_response(http.server.HTTPStatus.OK)
					if path in outer_self._mimetypes:
						self.send_header("Content-Type",outer_self._mimetypes[path])
					self.end_headers()
					self.wfile.write(response)
				except KeyError:
					self.send_error(404)
					self.end_headers()
				
		self._reqhandler=ReqHandler
		
	def put_data(self,k,v,mimetype=None):
		self._serve_data[k]=v
		if mimetype is not None:
			self._mimetypes[k]=mimetype
	def put_image(self,k,img):
		bio=io.BytesIO()
		img.convert("RGB").save(bio,format="JPEG")
		self.put_data(k,bio.getvalue(),"image/jpeg")
	def put_string(self,k,s):
		self.put_data(k,s.encode(),"text/plain")
	def put_json(self,k,d):
		bio=io.StringIO()
		json.dump(d,bio)
		self.put_data(k,bio.getvalue().encode(),"text/javascript")
	def _get_data(self,k):
		return self._serve_data[k]
		
	def run(self):
		print("Server thread started")
		self._serv=http.server.ThreadingHTTPServer(('',self._port),self._reqhandler)
		self._serv.serve_forever()
		print("Server thread stopped")
	def die(self):
		self._serv.shutdown()
	
if __name__=="__main__":
	# Testing
	st=ServerThread(28301)
	st.put_string("/","asdf")
	st.start()
	for i in range(10):
		print(i)
		time.sleep(1)
	st.die()
