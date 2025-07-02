from PySide6.QtCore import QObject, Slot as pyqtSlot, Signal as pyqtSignal, Property as pyqtProperty
import yaml
import os

class ServiceSettingModel(QObject):
    serviceChanged = pyqtSignal(str, str)  # module, service_id
    fieldChanged = pyqtSignal(str, str, str)  # module, key, value

    def __init__(self, config_path, settings_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.settings_path = settings_path
        self._load_config()
        self._load_settings()

    def _load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def _load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                self.settings = yaml.safe_load(f)
        else:
            self.settings = {}

        for module, services in self.config.items():
            if module not in self.settings:
                self.settings[module] = {'selected': '', 'settings': {}}
            if 'settings' not in self.settings[module] or \
                not isinstance(self.settings[module]['settings'], dict):
                self.settings[module]['settings'] = {}

            for service in services:
                service_id = service['id']
                if service_id not in self.settings[module]['settings']:
                    self.settings[module]['settings'][service_id] = {}
        self._save_settings()

    @pyqtSlot(str, result='QVariant')
    def getServiceList(self, module):
        return self.config.get(module, [])

    @pyqtSlot(str, result=str)
    def getSelectedService(self, module):
        return self.settings.get(module, {}).get('selected', '')

    @pyqtSlot(str, str, result='QVariant')
    def getServiceFields(self, module, service_id):
        for s in self.config.get(module, []):
            if s['id'] == service_id:
                schema_path = s['schema']
                break
        else:
            return []
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)
        return schema.get('fields', [])

    @pyqtSlot(str, str, result=str)
    def getFieldValue(self, module, key):
        selected = self.getSelectedService(module)
        # Try to get value from settings
        val = self.settings.get(module, {}).get('settings', {}).get(selected, {}).get(key, None)
        if val is not None and val != '':
            return val
        # If not found, get default from schema
        service_id = selected
        schema_fields = self.getServiceFields(module, service_id)
        for field in schema_fields:
            if field.get('key') == key:
                return str(field.get('default', ''))
        return ''

    @pyqtSlot(str, str)
    def setSelectedService(self, module, service_id):
        current = self.settings.get(module, {}).get('selected', None)
        if current == service_id:
            return
        if module not in self.settings:
            self.settings[module] = {'selected': service_id, 'settings': {}}
        else:
            self.settings[module]['selected'] = service_id
        self._save_settings()
        self.serviceChanged.emit(module, service_id)

    @pyqtSlot(str, str, str)
    def setFieldValue(self, module, key, value):
        selected = self.getSelectedService(module)
        if module not in self.settings:
            self.settings[module] = {'selected': selected, 'settings': {}}
        if selected not in self.settings[module]['settings']:
            self.settings[module]['settings'][selected] = {}
        current = self.settings[module]['settings'][selected].get(key, None)
        if current == value:
            return
        self.settings[module]['settings'][selected][key] = value
        self._save_settings()
        self.fieldChanged.emit(module, key, value)

    def _save_settings(self):
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.settings, f, allow_unicode=True)
