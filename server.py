#!/usr/bin/python
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from os import curdir, sep
import cgi
import transformer
import traceback

PORT_NUMBER = 8000

#This class will handles any incoming request from
#the browser 
class RedVisHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		if self.path=="/":
			self.path="/subreddit-interactions.html"

		try:
			#Check the file extension required and
			#set the right mime type

			if self.path.endswith(".html"):
				mimetype='text/html'
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
			if self.path.endswith(".gif"):
				mimetype='image/gif'
			if self.path.endswith(".js"):
				mimetype='application/javascript'
			if self.path.endswith(".css"):
				mimetype='text/css'
			if self.path.endswith(".json"):
				mimetype='application/json'

			if mimetype:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) 
				self.send_response(200)
				self.send_header('Content-type',mimetype)
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#Handler for the POST requests
	def do_POST(self):
		if self.path=="/filter":
			try:
				form = cgi.FieldStorage(
					fp=self.rfile, 
					headers=self.headers,
					environ={'REQUEST_METHOD':'POST',
						 'CONTENT_TYPE':self.headers['Content-Type'],
				})
	
				print "Filter triggered with:"
	
				form_edge = form["edge_value"]
				if(form_edge):
					print "Min edge value: %s" % form_edge.value
					edge_value = form_edge.value
				else:
					edge_value = 70 # Default threshold
	
				form_subm = form["sub_max"]
				if(form_subm):
					print "Subreddit: %s" % form_subm.value
					sub_max = form_subm.value
				else:
					sub_max = 0
	
				form_subn = form["sub_name"] if ("sub_name" in form) else False
				if(form_subn):
					print "Subreddit: %s" % form_subn.value
					sub_name = form_subn.value
				else:
					sub_name = ""
	
				transformer.construct_graph('results.json', edge_value, sub_max, False)
	
				self.send_response(200)
				self.end_headers()
				self.wfile.write("Filtering complete.")
				return			
			except Exception as ex:
				print traceback.format_exc()
				self.send_response(500)
				self.end_headers()
				self.wfile.write("Internal Server Error")
				return

			
			
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), RedVisHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
