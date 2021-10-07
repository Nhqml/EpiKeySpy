from .devices import list_devices, list_supported_devices

devices = list_supported_devices()
devices[0].capture_events()
