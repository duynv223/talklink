from PySide6.QtCore import QObject, Signal, Slot, Property
from vpipe.utils.audio_devices import list_input_devices, list_output_devices

class AudioDeviceManager(QObject):
    devicesChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_devices = []
        self._output_devices = []
        self.refresh()

    @Slot()
    def refresh(self):
        self._input_devices = [
            {"name": name, "index": idx}
            for idx, name in list_input_devices()
        ]
        self._output_devices = [
            {"name": name, "index": idx}
            for idx, name in list_output_devices()
        ]
        self.devicesChanged.emit()

    @Property('QVariant', notify=devicesChanged)
    def inputDevices(self):
        return self._input_devices

    @Property('QVariant', notify=devicesChanged)
    def outputDevices(self):
        return self._output_devices

    @Slot(result='QVariant')
    def get_input_devices(self):
        return self._input_devices

    @Slot(result='QVariant')
    def get_output_devices(self):
        return self._output_devices
