#!venv/bin/python

from http.server import HTTPServer, SimpleHTTPRequestHandler
from logging.handlers import QueueHandler
from signal import signal, SIGTERM
from sys import exit
import json
import logging
import sqlite3
import ssl
import urllib.parse

root = logging.getLogger()
root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)

def term_handler(signum, _):
    logger.info("Recieved SIGTERM. Stopping")
    exit(0)


class MyHTTPHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path == "/":
            self.wfile.write(open("post.html", "r").read().encode("utf-8"))

        else:
            self.wfile.write("""<!DOCTYPE html>
                <html>
                <head>
                    <title>Auth system</title>
                    <meta charset="utf-8">
                </head>
                <body>
                    <h1>Auth system</h1>
                    <p>You asked the path: <code>{}</code></p>
                    <p>This service should be used with a POST method !</p>
                </body>
                </html>
            """.format(self.path).encode("utf-8"))

    def do_POST(self):
        if "Content-Length" not in self.headers:
            self.my_send_error(411, "Length Required", "The 'Content-Length' is required")
            return

        length = int(self.headers['Content-Length'])
        try:
            post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))
        except Exception as ex:
            self.my_send_error(400, "Bad request", "Please check your request", str(ex))
            return

        funcdict = {
            "/register": self.register,
            "/authenticate": self.authenticate,
            "/refresh": self.refresh,
            "/validate": self.validate,
            "/invalidate": self.invalidate,
            "/signout": self.signout
            }

        if self.path in funcdict:
            print(post_data)
            funcdict[self.path](post_data)
            return
        else:
            self.my_send_error(404, "Service not found", "The URI is not valid: {}".format(self.path))
            return

    def log_message(self, frm, *args):
        logging.info(frm, *args)

    def register(self, data):
        pass

    def authenticate(self, data):
        pass

    def refresh(self, data):
        pass

    def validate(self, data):
        pass

    def invalidate(self, data):
        pass

    def signout(self, data):
        pass

    def my_send_error(self, code, error, error_message, cause=None):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        d = {
            "error": error,
            "errorMessage": error_message
        }
        if cause is not None:
            d["cause"] = str(cause) if isinstance(cause, Exception) else cause

        self.wfile.write(json.dumps(d).encode("utf-8"))

def start(host, port, cert_path, key_path, queue):

    signal(SIGTERM, term_handler)

    root.addHandler(QueueHandler(queue))

    logger.info("Auth server listening on https://%s:%d", host, port)
    httpd = HTTPServer((host, port), MyHTTPHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_path, keyfile=key_path, server_side=True)
    try:
        httpd.serve_forever()
    except Exception as ex:
        logger.critical("Auth server stopped working !", exc_info=ex)
        exit(1)
