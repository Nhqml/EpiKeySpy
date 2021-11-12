from __future__ import annotations

import enum
import re
from enum import Enum
from pathlib import Path
from typing import Optional

from .events import Event

DEVICES_PATH = Path('/proc/bus/input/devices')
HANDLERS_PATH = Path('/dev/input')


class Device:
    """
    Input device, such as a keyboard, a mouse, etc.
    """
    class Type(Enum):
        """
        Enum of device types.
        """
        UNKNOWN = False  # Explicitely set to False (otherwise enum values are True)

        KEYBOARD = enum.auto()

        UNSUPPORTED = enum.auto()

        def __str__(self):
            return f'{self.name}'

    def __init__(self, name: str, type_: Type, handlers: list[str]) -> None:
        self.name = name
        self.type_ = type_
        self.handlers = handlers

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}', type={self.type_}, handlers={self.handlers}>"

    DEVICES_KNOWN_EVENTS = {
        Type.KEYBOARD: [Event.Type.EV_SYN, Event.Type.EV_KEY, Event.Type.EV_MSC, Event.Type.EV_LED, Event.Type.EV_REP],
    }

    NAME_RE = re.compile('N: Name="(.*)"')
    SUPPORTED_HANDLERS_RE = [re.compile(handler) for handler in ['event[0-9]+']]
    EV_RE = re.compile('B: EV=([0-9A-Fa-f]+)')

    def capture_raw_events(self, handler: Optional[str] = None):
        if not handler:
            handler = self.handlers[0]

        if handler in self.handlers:
            with open(HANDLERS_PATH / handler, 'rb') as events:
                while True:
                    yield events.read(Event.SIZE)
        else:
            raise ValueError(f'Invalid hander {handler} for device {self}')

    def capture_events(self, handler: Optional[str] = None):
        for raw_event in self.capture_raw_events():
            yield Event.from_raw(raw_event)

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
                    ev = int(match.group(1), base=16)

                    # Retrieve all events supported by the device
                    events = []
                    for type_ in Event.Type:
                        if bool(ev & (1 << type_.value)):
                            events.append(type_)

                    # Match events with known devices events
                    for dev_type, dev_events in cls.DEVICES_KNOWN_EVENTS.items():
                        # All events from the DEVICES_KNOWN_EVENTS must be supported by the device
                        if all(event in events for event in dev_events):
                            type_ = dev_type
                            break
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
