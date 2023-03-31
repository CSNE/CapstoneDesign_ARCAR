import http.server
import threading
import time
import io

class ServerThread(threading.Thread):
	def __init__(self,port):
		super().__init__()
		self._port=port
		self._serve_data=dict()
		
		outer_self=self
		class ReqHandler(http.server.BaseHTTPRequestHandler):
			def log_message(self, format, *args): #supress log messages
				return
			def do_GET(self):
				path=self.path.split("?")[0]
				client_addr, client_port=self.client_address
				print("GET on",path)
				print("from",client_addr)
				
				try:
					response=outer_self._get_data(path)
					self.send_response(http.server.HTTPStatus.OK)
					self.end_headers()
					self.wfile.write(response)
				except KeyError:
					self.send_error(404)
					self.end_headers()
				
		self._reqhandler=ReqHandler
		
	def put_data(self,k,v):
		self._serve_data[k]=v
	def put_image(self,k,img):
		bio=io.BytesIO()
		img.convert("RGB").save(bio,format="JPEG")
		self.put_data(k,bio.getvalue())
	def put_string(self,k,s):
		self.put_data(k,s.encode())
		
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
	
	with open("webpage.html","rb") as f:
		page=f.read()
	st=ServerThread(28301)
	st.put_data("/",page)
	st.put_data("/test","testdata".encode())
	st.start()
	for i in range(10):
		print(i)
		time.sleep(1)
	st.die()
