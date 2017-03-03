# -*- coding: utf-8 -*-
import json
import base64
from io import BytesIO

from sphinxcontrib.httpexample.utils import ordered

try:
    from http.server import BaseHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler


class HTTPRequest(BaseHTTPRequestHandler):
    # http://stackoverflow.com/a/5955949

    scheme = 'http'

    # noinspection PyMissingConstructor
    def __init__(self, request_bytes):
        assert isinstance(request_bytes, bytes)

        self.rfile = BytesIO(request_bytes)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message=None, explain=None):
        self.error_code = code
        self.error_message = message

    def auth(self):
        try:
            method, token = self.headers.get('Authorization').split()
        except ValueError:
            return None, None
        if not isinstance(token, bytes):
            token = token.encode('utf-8')
        if method == 'Basic':
            return method, base64.b64decode(token).decode('utf-8')
        else:
            return method, token

    def url(self):
        return '{}://{}{}'.format(
            self.scheme,
            self.headers.get('Host', 'nohost'),
            self.path
        )

    def data(self):
        assert self.headers.get('Content-Type') == 'application/json'
        payload_bytes = self.rfile.read()
        assert isinstance(payload_bytes, bytes)
        payload_str = payload_bytes.decode('utf-8')
        return ordered(json.loads(payload_str))


def parse_request(request_bytes):
    return HTTPRequest(request_bytes)