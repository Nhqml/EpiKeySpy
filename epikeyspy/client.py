from .devices import list_devices, list_supported_devices


def client_loop(server: str):
    devices = list_supported_devices()
    for event in devices[0].capture_events():
        print(event)
