import sys
from http.client import HTTPConnection
from pickle import dumps
from urllib.parse import urlparse

from .devices import list_devices, list_supported_devices


def client_loop(dev_id: int, server: str, raw: bool):
    try:
        device = list_supported_devices()[dev_id]
    except IndexError:
        print('Invalid device selected', file=sys.stderr)
        sys.exit(1)

    events = device.capture_raw_events() if raw else device.capture_events()
    urlp = urlparse('//' + server)

    try:
        for event in events:
            conn = HTTPConnection(urlp.hostname, urlp.port)

            try:
                if raw:
                    conn.request('POST', '/', body=event, headers={'data-format': 'raw'})
                else:
                    conn.request('POST', '/', body=dumps(event), headers={'data-format': 'no-raw'})

                resp = conn.getresponse()
                if resp.status >= 400:
                    raise Exception('Something went wrong')
            except ConnectionRefusedError:
                print('Warning: unable to send data to server')
    except ConnectionResetError:
        pass
