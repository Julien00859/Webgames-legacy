from logging import getLogger
from time import sleep
from http.server import HTTPServer, BaseHTTPRequestHandler

from models import Session
from settings import *

class AuthHandler(BaseHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		super().__init__(self, request, client_address, server)
		self.session = Session()

	def do_POST(self):
		print("Plop")
		pass

	def do_GET(self):
		print("Plop")
		pass



logger = getLogger(__name__)


def start(queue):
	logger.info("In Auth Server")
	http = HTTPServer((AUTH_HOST, AUTH_PORT), AuthHandler)
	http.serve_forever()
