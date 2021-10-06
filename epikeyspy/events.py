from enum import IntFlag


class EventType(IntFlag):
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
