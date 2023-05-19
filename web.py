# Webserver-related code

import http.server
import threading
import time
import io
import json
import urllib.parse
import collections
import sys

import PIL.Image

class ErrorSupressedServer(http.server.ThreadingHTTPServer):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,*kwargs)
	def handle_error(self, request, client_address):
		# Override from BaseServer from Lib/socketserver.py
		exc_type,exc,tb=sys.exc_info()
		print(F"{exc_type.__name__} on server. Ignoring.")

WebResponse=collections.namedtuple(
	"WebResponse",
	["content","mimetype"])

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

	Set custom handler with
	st.set_handler("/dynamic",lambda q: WebResponse(content=F"Query:{q}".encode(),mimetype="text/plain"))

	now server will reply with the query string when you access /dynamic
	'''
	def __init__(self,port):
		super().__init__()
		self._port=port
		self._handlers=dict()
		self._serv=None
		
		outer_self=self
		class ReqHandler(http.server.BaseHTTPRequestHandler):
			def log_message(self, format, *args): #supress log messages
				return
			def do_GET(self):
				parsed_path=urllib.parse.urlparse(self.path)
				#print(parsed_path)
				path=parsed_path.path
				qs=urllib.parse.parse_qs(parsed_path.query)
				#print(qs)

				client_addr, client_port=self.client_address
				
				if path in outer_self._handlers:
					wr=outer_self._handlers[path](qs)

					self.send_response(http.server.HTTPStatus.OK)
					if wr is None:
						# If we don't do this, the XMLHttpRequest will complain
						# about XML parse errors
						self.send_header("Content-Type","text/plain")
						self.end_headers()
					else:
						if wr.mimetype is not None:
							self.send_header("Content-Type",wr.mimetype)
						self.end_headers()
						self.wfile.write(wr.content)
				else:
					self.send_error(404)
					self.end_headers()
				
		self._reqhandler=ReqHandler

	def put_data(self,k,v,mimetype=None):
		if v is None:
			self.clear_data(k)
			return
		resp= WebResponse(content=v,mimetype=mimetype)
		self.set_handler(k,lambda q: resp)
	def clear_data(self,k):
		self.clear_handler(k)

	def put_image(self,k,img):
		if img is None:
			self.clear_data(k)
			return
		bio=io.BytesIO()
		img.convert("RGB").save(bio,format="JPEG")
		self.put_data(k,bio.getvalue(),"image/jpeg")
	def put_string(self,k,s):
		if s is None:
			self.clear_data(k)
			return
		self.put_data(k,s.encode(),"text/plain")
	def put_json(self,k,d):
		if d is None:
			self.clear_data(k)
			return
		bio=io.StringIO()
		json.dump(d,bio)
		self.put_data(k,bio.getvalue().encode(),"text/javascript")

	def set_handler(self,path,f):
		'''
		Set handler for a path. f should be a function that
		takes a dict of query, and (optinally) returns a webpage.
		This has priority over regular data.
		'''
		self._handlers[path]=f
	def clear_handler(self,path):
		if path in self._handlers:
			del self._handlers[path]
		
	def run(self):
		#print("Server thread started")
		self._serv=ErrorSupressedServer(('',self._port),self._reqhandler)
		self._serv.serve_forever()
		#print("Server thread stopped")
	def die(self):
		if self._serv is not None:
			print("Killing server...")
			self._serv.shutdown()
	
if __name__=="__main__":
	# Testing
	st=ServerThread(28301)
	st.put_string("/","asdf")
	st.set_handler("/dynamic",lambda q: WebResponse(content=F"Query:{q}".encode(),mimetype="text/plain"))
	st.start()
	for i in range(10):
		print(i)
		time.sleep(1)
	st.die()
