from PySide6.QtCore import QObject, Signal, Slot
import yaml
import os

"""
Not using singleton allows for greater flexibility, easier dependency management,
and better support for multiple configuration contexts within the same application.
"""

class SettingModel(QObject):
    valueChanged = Signal(str, 'QVariant')

    def __init__(self, filepath="setting.yaml"):
        super().__init__()
        self._filepath = filepath
        self._data = {}

        self._default_data = {
            "conference": {
                "your_lang": "vi",
                "other_lang": "en",
                "volume": {
                    "original": 1.0,
                    "translated": 1.0
                },
                "upstream": {
                    "asr_enable": True,
                    "tts_enable": True
                },
                "downstream": {
                    "asr_enable": True,
                    "tts_enable": True
                }
            },
            "directalk": {
                "src_lang": "en",
                "dest_lang": "vi",
                "volume": {
                    "original": 1.0,
                    "translated": 1.0
                }
            }
        }

    def load(self):
        if os.path.exists(self._filepath):
            with open(self._filepath, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f)
        else:
            self._data = self._default_data.copy()

    def save(self):
        with open(self._filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(self._data, f, allow_unicode=True)

    @Slot(str, result='QVariant')
    def get(self, path: str):
        parts = path.split(".")
        d = self._data
        for p in parts:
            d = d[p]

        return d

    @Slot(str, "QVariant")
    def set(self, path: str, value):
        parts = path.split(".")
        d = self._data
        for p in parts[:-1]:
            d = d[p]
        key = parts[-1]
        if d[key] != value:
            d[key] = value
            self.valueChanged.emit(path, value)
            self.save() # todo: adjust save policy

    def get_all(self):
        return self._data
