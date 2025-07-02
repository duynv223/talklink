import yaml
import importlib

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ServiceManager(metaclass=SingletonMeta):
    def __init__(self, config_path, settings_path):
        self.config = self._load_yaml(config_path)
        self.settings_path = settings_path
        self.settings = self._load_yaml(settings_path)
        self.instances = {}

    def _load_yaml(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_service_class(self, module, service_id):
        for service in self.config[module]:
            if service['id'] == service_id:
                module_name, class_name = service['class'].rsplit('.', 1)
                return getattr(importlib.import_module(module_name), class_name)
        raise ValueError(f"Service {service_id} not found in {module}")

    def get_service_settings(self, module, service_id):
        return self.settings[module]['settings'].get(service_id, {})

    def get_selected_service_id(self, module):
        return self.settings[module]['selected']

    def get_service_instance(self, module):
        service_id = self.get_selected_service_id(module)
        service_cls = self.get_service_class(module, service_id)
        kwargs = self.get_service_settings(module, service_id)
        if module == 'ASR':
            kwargs.setdefault('lang', self.settings.get('src_lang', 'en'))
        if module == 'TTS':
            kwargs.setdefault('lang', self.settings.get('dest_lang', 'vi'))
        instance = service_cls(**kwargs)
        self.instances[module] = instance
        return instance

    def reload_settings(self):
        self.settings = self._load_yaml(self.settings_path)
