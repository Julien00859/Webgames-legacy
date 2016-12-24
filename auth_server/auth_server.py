#!venv/bin/python

from logging import getLogger, basicConfig, DEBUG
from time import sleep
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import fstat
from shutil import copyfileobj
import json
from os import urandom
from binascii import hexlify
from threading import Thread
from sqlalchemy import or_
from ssl import wrap_socket
from signal import signal, SIGTERM

from models import Session, User
from settings import *
from auth_server.token_manager import *


session = Session()
@synchronized
def getSession():
	return session


class AuthHandler(BaseHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		super().__init__(request, client_address, server)

	def stop():
		self.running = False

	def do_GET(self):

		if self.path == "/" or "/index" or "/index.html":
			html = open("auth_server/index.html", "rb")
			fs = fstat(html.fileno())

			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.send_header("Content-length", str(fs.st_size))
			self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
			self.end_headers()
			copyfileobj(html, self.wfile)
			return

		else:
			self.send_response(HTTPStatus.NOT_FOUND)
			self.end_headers()
			return


	def do_POST(self):
		logger.debug("Path: %s", self.path)
		logger.debug("Headers: %s", ", ".join(map(lambda x: x + ": " + self.headers[x], self.headers)))
		if "Content-Length" not in self.headers or not self.headers["Content-Length"].isdigit():
			self.send_response(HTTPStatus.LENGTH_REQUIRED)
			return

		if "Content-Type" not in self.headers or self.headers["Content-Type"] != "application/json":
			self.send_response(HTTPStatus.NOT_ACCEPTABLE)
			return

		try:
			length = int(self.headers['Content-Length'])
			post_data = json.loads(self.rfile.read(length).decode("UTF-8"))
			if self.path == "/signin":
				print("!")
				self.signin(post_data["username"], post_data["password"])
		except:
			logger.exception("Invalid POST request")
			self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

	def signin(self, username: str, password: str) -> None:
		user = getSession().query(User).filter((User.u_name == username) | (User.u_email == username)).one_or_none()
		if user is None:
			self.send_response(404)
		else:
			self.send_response(200)
			self.send_header("Content-Type", "text/plain")
			self.send_header("Content-Length", str(AUTH_TOKEN_LENGTH * 2))
			self.end_headers()

			logger.info("%s successfully connected", username)
			token = hexlify(urandom(AUTH_TOKEN_LENGTH))
			add_token(token.decode())
			self.wfile.write(token)







logger = getLogger(__name__)


def start():
	logger.info("In Auth Server")
	http = HTTPServer((AUTH_HOST, AUTH_PORT), AuthHandler)
	http.allow_reuse_address = True
	http.socket = wrap_socket(http.socket, keyfile=AUTH_KEY_PATH, certfile=AUTH_CERT_PATH, server_side=True)
	
	def stop(signum, _):
		http.shutdown()
	signal(SIGTERM, stop)

	for worker in range(AUTH_WORKER_COUNT - 1):
		Thread(target=http.serve_forever).start()
	http.serve_forever()
