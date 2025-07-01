import logging


class VpLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, vpobject):
        super().__init__(logger, {})
        self.vpobject = vpobject

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        extra.update({
            "obj_cls": self.vpobject.__class__.__name__,
            "obj_name": self.vpobject.name,
            "obj_path": self.vpobject.path
        })
        kwargs["extra"] = extra
        return msg, kwargs


class VpObject:
    def __init__(self, name=None):
        self._name = name or self.__class__.__name__
        self._parent = None
        self._properties = {}
        self._signals = {}
        base_logger = logging.getLogger("vpobj")
        self.logger = VpLoggerAdapter(base_logger, self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def path(self):
        parts = []
        current = self
        while current is not None:
            parts.append(current.name)
            current = getattr(current, "parent", None)
        return "/".join(reversed(parts))

    def set_property(self, key, value):
        self._properties[key] = value

    def get_property(self, key):
        return self._properties.get(key)

    def connect_signal(self, signal_name, callback):
        self._signals.setdefault(signal_name, []).append(callback)

    def emit_signal(self, signal_name, *args, **kwargs):
        for callback in self._signals.get(signal_name, []):
            callback(*args, **kwargs)
