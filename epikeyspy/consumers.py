"""
Define your own consumers function here and add them to the `_consumers_` list.
"""

from .events import Event, EventKey

CONSUMERS = ['multiple_keys']


def print_keys(event: Event) -> None:
    """Prints KEY events only.
    """
    if event.type_ is Event.Type.EV_KEY:
        print(event)


__active_keys = set()


def multiple_keys(event: Event) -> None:
    """Prints KEY events and interpret key combinations.
    """
    if event.type_ is Event.Type.EV_KEY:
        if event.value is EventKey.Value.PRESSED:
            __active_keys.add(event.code)
        elif event.value is EventKey.Value.RELEASED:
            print(' + '.join(map(lambda key: key.name, __active_keys)))
            __active_keys.remove(event.code)
