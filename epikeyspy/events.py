from __future__ import annotations

import struct
from datetime import datetime, timedelta
from enum import IntFlag


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
        EV_SYN = 0x00  # Event separator
        EV_KEY = 0x01  # Key-like devices (e.g. keyboard)
        EV_REL = 0x02  # Relative axis value change
        EV_ABS = 0x03  # Absolute axis value change
        EV_MSC = 0x04  # Misc
        EV_SW = 0x05  # Binary state input switch
        EV_LED = 0x11  # LEDs control
        EV_SND = 0x12  # Send sound
        EV_REP = 0x14  # Autorepeating devices
        EV_FF = 0x15  # Send force feedback
        EV_PWR = 0x16  # Power button / switch input
        EV_FF_STATUS = 0x17  # Receive force feedback status

        def __str__(self):
            return f'{self.name}'

    FORMAT = 'QQHHI'  # 24 bytes long: 2 unsigned long long, 2 unsigned short, 1 unsigned int
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, datetime, type_, code, value) -> None:
        self.datetime = datetime
        self.type_ = type_
        self.code = code
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} datetime={self.datetime}, type={self.type_}, code={self.code}, value={self.value}>"

    @classmethod
    def from_raw(cls, raw_event: list[str]) -> Event:
        sec, usec, type_, code, value = struct.unpack(Event.FORMAT, raw_event)
        return Event(datetime.fromtimestamp(sec) + timedelta(microseconds=usec), cls.Type(type_), code, value)
