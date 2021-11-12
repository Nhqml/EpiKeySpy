from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus


class Handler(BaseHTTPRequestHandler):
    def send_response(self, code, message=None):
        """Overrides super class method to get rid of the call to `log_request`.
        """
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def do_POST(self):
        print(self.rfile.read(int(self.headers.get('Content-Length'))))
        self.send_response(HTTPStatus.IM_A_TEAPOT)
        self.end_headers()


def server_loop(address: str, port: int):
    server = HTTPServer((address, port), Handler)
    server.serve_forever()
