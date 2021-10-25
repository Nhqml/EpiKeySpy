from .devices import list_devices, list_supported_devices


def client_loop(server: str):
    devices = list_supported_devices()
    devices[0].capture_events()
