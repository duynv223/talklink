class VpObject:
    def __init__(self, name=None):
        self._name = name or self.__class__.__name__
        self._properties = {}
        self._signals = {}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def set_property(self, key, value):
        self._properties[key] = value

    def get_property(self, key):
        return self._properties.get(key)

    def connect_signal(self, signal_name, callback):
        self._signals.setdefault(signal_name, []).append(callback)

    def emit_signal(self, signal_name, *args, **kwargs):
        for callback in self._signals.get(signal_name, []):
            callback(*args, **kwargs)
