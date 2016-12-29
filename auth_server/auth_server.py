#!venv/bin/python

from datetime import datetime
from hashlib import sha256
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from logging import getLogger
from os import fstat
from shutil import copyfileobj
from signal import signal, SIGTERM
from ssl import wrap_socket
from threading import Thread, Lock
import json

from wrapt import synchronized

from auth_server.tokens import Tokens
from auth_server import attemps
from models import Session, User
from settings import *


logger = getLogger(__name__)
threads = []

session = Session()
sessionLock = Lock()
def getSession():
	with sessionLock:
		return session

userTokens = Tokens()
registerTokens = Tokens()

class AuthHandler(BaseHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		super().__init__(request, client_address, server)

	def stop():
		self.running = False

	def do_GET(self):

		if self.path == "/":
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


	def fail(self, code: HTTPStatus, error:str=None, message:str=None, cause:str=None):
		data = {
			"error": error if error is not None else code.phrase,
			"errorMessage": message if message is not None else code.description,
			}
		if cause is not None:
			data["cause"] = cause
		json_data = json.dumps(data)

		self.send_response(code)
		self.send_header("Content-Type", "application/json")
		self.send_header("Content-Length", str(len(json_data)))
		self.end_headers()
		self.wfile.write(json_data)


	def do_POST(self):
		logger.debug("Path: %s", self.path)
		logger.debug("Headers:%s", "\n\t".join(map(lambda h, v: h + ": " + v, self.headers.items())))

		length = self.headers.get("Content-Length")
		if length is None:
			self.fail(HTTPStatus.LENGTH_REQUIRED)
			return

		ctype = self.headers.get("Content-Type")
		if ctype is None or ctype != "application/json":
			self.fail(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, cause="Invalid header")
			return

		try:
			post_data = json.loads(self.rfile.read(length).decode("UTF-8"))
		except json.JSONDecodeError as ex:
			self.fail(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, cause="{msg} ({lineno}:{colno})".format(**ex))
			return

		if self.path == "/signin":
			login = post_data.get("login")
			password = post_data.get("password")
			if None in  [login, password]:
				self.fail(HTTPStatus.BAD_REQUEST, cause="Login or password absent from the request")
				return

			self.signin(login, password)

		elif self.path == "/signup":
			username = post_data.get("username")
			email = post_data.get("email")
			password = post_data.get("password")
			if None in [username, email, password]:
				self.fail(HTTPStatus.BAD_REQUEST, cause="Login or password absent from the request")
				return

			self.signup(username, email, password)

		elif self.path == "/refresh":
			token = post_data.get("token")
			if token is None:
				self.fail(HTTPStatus.BAD_REQUEST, cause="Token absent from the request")
				return

			self.refresh(token)

		elif self.path == "/invalidate":
			token = post_data.get("token")
			if token is None:
				self.fail(HTTPStatus.BAD_REQUEST, cause="Token absent from the request")
				return

			self.invalidate(token)

		elif self.path == "/signout":
			login = post_data.get("login")
			password = post_data.get("password")
			if None in  [login, password]:
				self.fail(HTTPStatus.BAD_REQUEST, cause="Login or password absent from the request")
				return

			self.signout(login, password)


	def signin(self, login: str, password: str):
		attemp = attemps.get(login, self.client_address[0])

		if attemp.count > 0 and attemp.last_try + attemps.totime(attemp.count) > datetime.utcnow():
			self.fail(HTTPStatus.UNAUTHORIZED, "Too many attemps", "This account is locked until " + str(attemp.last_try + attemps.totime(attemp.count)))
			return

		user = getSession().query(User).filter((User.username == login) | (User.email == login)).one_or_none()
		if user is None:
			self.fail(HTTPStatus.NOT_FOUND, message="User not found")
			return

		elif user.password == sha256(AUTH_PASSWORD_SALT + password.encode()).hexdigest():
			attemp.reset(login, self.client_address[0])
			try:
				token = userTokens.create(user.u_id)
			except RuntimeError:
				logger.error("No access token left (%d random generation tried)", AUTH_TOKEN_GENERATION_MAX_TRY)
				self.fail(HTTPStatus.INTERNAL_SERVER_ERROR, message="The auth server is under heavy charge, please retry later", cause="No access token available")
				if userTokens.lock.acquire(blocking=False):
					logger.warning("Use worker to free expirated tokens")
					userTokens.free(AUTH_TOKEN_FREE_TIMEOUT)
					userTokens.lock.release()

			self.send_response(HTTPStatus.OK)
			self.send_header("Content-Type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps({"accessToken": token}))

		else:
			attemps.incr(login, self.client_address[0])
			self.fail(HTTPStatus.UNAUTHORIZED, "Wrong password", "Wrong password")
			return

	def signup(self, username: str, email: str, password: str):
		logger.warning("Call this function thousand of times to break the system :D")

		user = getSession().query(User).filter((User.username == username) | (User.email == email)).one_or_none()
		if user is not None:
			self.fail(HTTPStatus.CONFLICT, cause="Username used already" if user.username == username else "Email used already")
			return

		try:
			new_user = User(u_name=username, u_email=email, u_password=sha256(AUTH_PASSWORD_SALT + password.encode()).hexlify())
		except Exception as ex:
			self.fail(HTTPStatus.BAD_REQUEST, cause=str(ex))

		getSession().add(new_user)

		self.send_response(HTTPStatus.NO_CONTENT)

	def refresh(self, token: str):
		if userTokens.isvalid(token):
			userTokens.refresh(token)
			self.send_response(HTTPStatus.NO_CONTENT)
		else:
			self.fail(HTTPStatus.UNAUTHORIZED, cause="Expirated")

	def invalidate(self, token: str):
		userTokens.remove(token)
		self.send_response(HTTPStatus.NO_CONTENT)


	def signout(self, login: str, password: str):
		attemp = attemps.get(login, self.client_address[0])

		if attemp.count > 0 and attemp.last_try + attemps.totime(attemp.count) > datetime.utcnow():
			self.fail(HTTPStatus.UNAUTHORIZED, "Too many attemps", "This account is locked until " + str(attemp.last_try + attemps.totime(attemp.count)))
			return

		user = getSession().query(User).filter((User.username == login) | (User.email == login)).one_or_none()
		if user is None:
			self.fail(HTTPStatus.NOT_FOUND, message="User not found")
			return

		elif user.password == sha256(AUTH_PASSWORD_SALT + password.encode()).hexdigest():
			attemp.reset(login, self.client_address[0])
			userTokens.remove_user(user.u_name)
			self.send_response(HTTPStatus.NO_CONTENT)
			return

		else:
			attemps.incr(login, self.client_address[0])
			self.fail(HTTPStatus.UNAUTHORIZED, "Wrong password", "Wrong password")
			return

def start():
	logger.info("Auth Server is available at https://%s:%d", AUTH_HOST, AUTH_PORT)

	http = HTTPServer((AUTH_HOST, AUTH_PORT), AuthHandler)
	http.allow_reuse_address = True
	http.socket = wrap_socket(http.socket, keyfile=AUTH_KEY_PATH, certfile=AUTH_CERT_PATH, server_side=True)
	
	def stop(signum, _):
		logger.info("Stopping...")
		http.shutdown()  # Stopped here ???
		for th in threads:
			th.join()
		getSession().commit()
		logger.info("Stopped")

	signal(SIGTERM, stop)
	logger.info("Process is now stoppable")

	for worker in range(AUTH_WORKER_COUNT - 1):
		logger.info("Start worker #%d", worker)
		th = Thread(target=http.serve_forever)
		th.start()
		threads.append(th)

	logger.info("Start worker #%s", AUTH_WORKER_COUNT)
	http.serve_forever()
