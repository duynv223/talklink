import unittest
from unittest.mock import patch
import sys
import types

from services.service_manager import ServiceManager

class DummyService:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class OtherService:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class DummyTTS:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class TestServiceManager(unittest.TestCase):
    def setUp(self):
        self.config = {
            'ASR': [
                {
                    'id': 'dummy',
                    'name': 'Dummy ASR',
                    'class': 'dummy_module.DummyService',
                    'schema': 'schemas/dummy_asr.sch.yaml',
                },
                {
                    'id': 'other',
                    'name': 'Other ASR',
                    'class': 'dummy_module.OtherService',
                    'schema': 'schemas/other_asr.sch.yaml',
                }
            ],
            'TTS': [
                {
                    'id': 'dummy_tts',
                    'name': 'Dummy TTS',
                    'class': 'dummy_module.DummyTTS',
                    'schema': 'schemas/dummy_tts.sch.yaml',
                }
            ]
        }
        self.settings = {
            'ASR': {
                'selected': 'other',
                'settings': {
                    'dummy': {'api_key': 'abc', 'lang': 'en'},
                    'other': {'api_key': 'xyz', 'lang': 'vi'}
                }
            },
            'TTS': {
                'selected': 'dummy_tts',
                'settings': {
                    'dummy_tts': {'voice': 'test'}
                }
            },
            'src_lang': 'en',
            'dest_lang': 'vi'
        }
        # Patch ServiceManager._load_yaml to return our config/settings
        self._load_yaml_patch = patch.object(ServiceManager, '_load_yaml', side_effect=[self.config, self.settings])
        self._load_yaml_patch.start()
        # Patch importlib.import_module to return a dummy module
        dummy_module = types.ModuleType('dummy_module')
        dummy_module.DummyService = DummyService
        dummy_module.OtherService = OtherService
        dummy_module.DummyTTS = DummyTTS
        sys.modules['dummy_module'] = dummy_module
        # Reset singleton instance before each test
        ServiceManager._instances = {}

    def tearDown(self):
        self._load_yaml_patch.stop()
        if 'dummy_module' in sys.modules:
            del sys.modules['dummy_module']
        ServiceManager._instances = {}

    def test_get_service_class(self):
        sm = ServiceManager('dummy_config.yaml', 'dummy_settings.yaml')
        cls = sm.get_service_class('ASR', 'dummy')
        self.assertIs(cls, DummyService)
        cls2 = sm.get_service_class('ASR', 'other')
        self.assertIs(cls2, OtherService)
        cls3 = sm.get_service_class('TTS', 'dummy_tts')
        self.assertIs(cls3, DummyTTS)

    def test_get_service_settings(self):
        sm = ServiceManager('dummy_config.yaml', 'dummy_settings.yaml')
        settings = sm.get_service_settings('ASR', 'dummy')
        self.assertEqual(settings, {'api_key': 'abc', 'lang': 'en'})
        settings2 = sm.get_service_settings('ASR', 'other')
        self.assertEqual(settings2, {'api_key': 'xyz', 'lang': 'vi'})
        settings3 = sm.get_service_settings('TTS', 'dummy_tts')
        self.assertEqual(settings3, {'voice': 'test'})

    def test_get_selected_service_id(self):
        sm = ServiceManager('dummy_config.yaml', 'dummy_settings.yaml')
        selected_asr = sm.get_selected_service_id('ASR')
        self.assertEqual(selected_asr, 'other')
        selected_tts = sm.get_selected_service_id('TTS')
        self.assertEqual(selected_tts, 'dummy_tts')

    def test_get_service_instance(self):
        sm = ServiceManager('dummy_config.yaml', 'dummy_settings.yaml')
        instance_asr = sm.get_service_instance('ASR')
        self.assertIsInstance(instance_asr, OtherService)
        self.assertEqual(instance_asr.kwargs['api_key'], 'xyz')
        self.assertEqual(instance_asr.kwargs['lang'], 'vi')
        instance_tts = sm.get_service_instance('TTS')
        self.assertIsInstance(instance_tts, DummyTTS)
        self.assertEqual(instance_tts.kwargs['voice'], 'test')
        self.assertEqual(instance_tts.kwargs['lang'], 'vi')

if __name__ == '__main__':
    unittest.main()
