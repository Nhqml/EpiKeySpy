import sys
import time
from http.client import HTTPConnection
from pickle import dumps
from urllib.parse import urlparse

from .devices import list_supported_devices


def client_loop(dev_id: int, server: str, raw: bool):
    try:
        device = list_supported_devices()[dev_id]
    except IndexError:
        print('Invalid device selected', file=sys.stderr)
        sys.exit(1)

    events = device.capture_raw_events() if raw else device.capture_events()
    urlp = urlparse('//' + server)

    conn = HTTPConnection(urlp.hostname, urlp.port)
    try:
        while True:
            try:
                conn.connect()
                print('Connected to server')
            except ConnectionRefusedError:
                print('Unable to connect to server', file=sys.stderr)
                time.sleep(1)
                continue

            try:
                for event in events:
                    if raw:
                        conn.request('POST', '/', body=event, headers={'data-format': 'raw'})
                    else:
                        conn.request('POST', '/', body=dumps(event), headers={'data-format': 'no-raw'})

                    resp = conn.getresponse()
                    if resp.status >= 400:
                        raise Exception('Something went wrong')
            except ConnectionResetError:
                print('Warning: Connection to server has been lost. Retrying to connect', file=sys.stderr)
    except KeyboardInterrupt:
        conn.close()
