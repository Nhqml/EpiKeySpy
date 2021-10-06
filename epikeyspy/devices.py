from __future__ import annotations

import enum
import re
from enum import Enum
from pathlib import Path

from .events import EventType

DEVICES_PATH = Path('/proc/bus/input/devices')


class Device():
    """
    Input device, such as a keyboard, a mouse, etc.
    """
    class Type(Enum):
        """
        Enum of device types.
        """
        UNKNOWN = False  # Explicitely set to False (otherwise enum values are True)

        UNSUPPORTED = enum.auto()
        KEYBOARD = enum.auto()

        def __str__(self):
            return f'{self.name}'

    def __init__(self, name: str, type_: Type, handlers: list[str]) -> None:
        self.name = name
        self.type_ = type_
        self.handlers = handlers

    def __repr__(self):
        return f"<Device: name='{self.name}', type={self.type_}, handlers={self.handlers}>"

    NAME_RE = re.compile('N: Name="(.*)"')
    SUPPORTED_HANDLERS_RE = [re.compile(handler) for handler in ['event[0-9]+']]
    EV_RE = re.compile('B: EV=([0-9A-Fa-f]+)')

    @classmethod
    def from_raw(cls, raw_dev: list[str]) -> Device:
        """Create a new Device from raw data (read from /proc/bus/input/devices)

        Args:
            raw (list[str]): properties of input device

        Returns:
            Device: created device
        """

        name = str(cls.Type.UNKNOWN)
        handlers: list[str] = []
        type_ = cls.Type.UNKNOWN

        for field in raw_dev:
            if name == str(cls.Type.UNKNOWN) and field.startswith('N:'):  # Name
                if match := cls.NAME_RE.search(field):
                    name = match.group(1)
            elif not handlers and field.startswith('H:'):  # Handlers
                for supported_handler_re in cls.SUPPORTED_HANDLERS_RE:
                    handlers.extend(supported_handler_re.findall(field))
            elif not type_.value and field.startswith('B:'):  # Bitmaps
                if match := cls.EV_RE.search(field):
                    events = EventType(int(match.group(1), base=16))
                    if events & EventType.EV_KEY and events & EventType.EV_REP:
                        type_ = cls.Type.KEYBOARD
                    else:
                        type_ = cls.Type.UNSUPPORTED
                else:
                    type_ = cls.Type.UNKNOWN

        return cls(name, type_, handlers)


def list_devices() -> list[Device]:
    """List all detected input devices.
    """
    devices = []
    try:
        with open(DEVICES_PATH, 'r', encoding='utf-8') as file_:
            raw_devices = file_.read().strip().split('\n\n')
            for device in map(lambda d: d.split('\n'), raw_devices):
                devices.append(Device.from_raw(device))
    except OSError:
        pass
    return devices


def list_supported_devices() -> list[Device]:
    """List all supported devices.
    """
    return list(
        filter(lambda device: device.type_ not in [Device.Type.UNKNOWN, Device.Type.UNSUPPORTED], list_devices()))
