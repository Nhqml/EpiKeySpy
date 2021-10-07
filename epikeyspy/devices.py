from __future__ import annotations

import enum
import re
import struct
from enum import Enum, IntFlag
from pathlib import Path
from typing import Optional

DEVICES_PATH = Path('/proc/bus/input/devices')
HANDLERS_PATH = Path('/dev/input')


class Event:
    """Input event.

    According to Linux kernel documentation, this is the following structure:
        struct input_event {
            struct timeval time;
            unsigned short type;
            unsigned short code;
            unsigned int value;
        };
    """
    class Type(IntFlag):
        """
        Enum of event types as provided by Linux Kernel.
        See https://www.kernel.org/doc/html/latest/input/event-codes.html#event-types
        """
        EV_SYN = 1 << 0x00  # Event separator
        EV_KEY = 1 << 0x01  # Key-like devices (e.g. keyboard)
        EV_REL = 1 << 0x02  # Relative axis value change
        EV_ABS = 1 << 0x03  # Absolute axis value change
        EV_MSC = 1 << 0x04  # Misc
        EV_SW = 1 << 0x05  # Binary state input switch
        EV_LED = 1 << 0x11  # LEDs control
        EV_SND = 1 << 0x12  # Send sound
        EV_REP = 1 << 0x14  # Autorepeating devices
        EV_FF = 1 << 0x15  # Send force feedback
        EV_PWR = 1 << 0x16  # Power button / switch input
        EV_FF_STATUS = 1 << 0x17  # Receive force feedback status

    FORMAT = 'QQHHI'  # 24 bytes long: 2 unsigned long long, 2 unsigned short, 1 unsigned int
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, type_, code, value) -> None:
        self._type = type_
        self.code = code
        self.value = value


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

    def capture_events(self, handler: Optional[str] = None):
        if not handler:
            handler = self.handlers[0]

        if handler in self.handlers:
            with open(HANDLERS_PATH / handler, 'rb') as events:
                while True:
                    raw_event = events.read(Event.SIZE)
                    _, _, type_, code, value = struct.unpack(Event.FORMAT, raw_event)
                    print(type_, code, value)
        else:
            raise ValueError(f'Invalid hander {handler} for device {self}')

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
                    events = Event.Type(int(match.group(1), base=16))
                    if events & Event.Type.EV_KEY and events & Event.Type.EV_REP:
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
