import os
import tempfile
import yaml
import unittest
from app.models.service_setting_model import ServiceSettingModel

CONFIG_YAML = '''
ASR:
  - id: google
    name: Google ASR
    schema: asr_google_schema.yaml
  - id: azure
    name: Azure ASR
    schema: asr_azure_schema.yaml
TTS:
  - id: google
    name: Google TTS
    schema: tts_google_schema.yaml
'''

ASR_GOOGLE_SCHEMA = '''
fields:
  - key: lang
    label: Language
    type: string
    default: en-US
  - key: sample_rate
    label: Sample Rate
    type: number
    default: 16000
'''

TTS_GOOGLE_SCHEMA = '''
fields:
  - key: voice
    label: Voice
    type: string
    default: en-US-Wavenet-A
'''

def write_temp_yaml(content, dir, filename):
    path = os.path.join(dir, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

class TestServiceSettingModel(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        tmpdir = self.tmpdir.name
        self.config_path = write_temp_yaml(CONFIG_YAML, tmpdir, 'config.yaml')
        self.asr_schema_path = write_temp_yaml(ASR_GOOGLE_SCHEMA, tmpdir, 'asr_google_schema.yaml')
        self.tts_schema_path = write_temp_yaml(TTS_GOOGLE_SCHEMA, tmpdir, 'tts_google_schema.yaml')
        # Patch schema paths in config
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        config['ASR'][0]['schema'] = self.asr_schema_path
        config['TTS'][0]['schema'] = self.tts_schema_path
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config, f)
        self.settings_path = os.path.join(tmpdir, 'settings.yaml')
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump({}, f)
        self.model = ServiceSettingModel(self.config_path, self.settings_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_get_service_list(self):
        asr_list = self.model.getServiceList('ASR')
        self.assertIsInstance(asr_list, list)
        self.assertEqual(asr_list[0]['id'], 'google')

    def test_selected_service(self):
        self.assertEqual(self.model.getSelectedService('ASR'), '')
        self.model.setSelectedService('ASR', 'google')
        self.assertEqual(self.model.getSelectedService('ASR'), 'google')

    def test_get_service_fields(self):
        self.model.setSelectedService('ASR', 'google')
        fields = self.model.getServiceFields('ASR', 'google')
        self.assertIsInstance(fields, list)
        self.assertEqual(fields[0]['key'], 'lang')

    def test_get_and_set_field_value(self):
        self.model.setSelectedService('ASR', 'google')
        val = self.model.getFieldValue('ASR', 'lang')
        self.assertEqual(val, 'en-US')
        self.model.setFieldValue('ASR', 'lang', 'vi-VN')
        self.assertEqual(self.model.getFieldValue('ASR', 'lang'), 'vi-VN')
        self.model.setSelectedService('TTS', 'google')
        self.assertEqual(self.model.getFieldValue('TTS', 'voice'), 'en-US-Wavenet-A')
        self.model.setFieldValue('TTS', 'voice', 'vi-VN-Wavenet-B')
        self.assertEqual(self.model.getFieldValue('TTS', 'voice'), 'vi-VN-Wavenet-B')

if __name__ == '__main__':
    unittest.main()
