from PySide6.QtCore import QObject, Signal


class EventDispatcher(QObject):
    update_stats = Signal(dict)
    increment_stat = Signal(str)
    overwrite_stat = Signal(str, object)  # Updated to accept two arguments


# Create a single instance of the dispatcher
event_dispatcher = EventDispatcher()
