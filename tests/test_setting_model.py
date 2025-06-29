import unittest
import os
import yaml
from app.models.setting_model import SettingModel

class TestSettingModel(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_setting.yaml"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.model = SettingModel(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_default_data(self):
        self.model.load()
        data = self.model.get_all()
        self.assertIn("conference", data)
        self.assertIn("directalk", data)

    def test_save_and_load(self):
        self.model.load()
        self.model.set("conference.your_lang", "en")
        self.model.save()
        model2 = SettingModel(filepath=self.test_file)
        model2.load()
        self.assertEqual(model2.get("conference.your_lang"), "en")

    def test_get_set(self):
        self.model.load()
        self.model.set("conference.upstream.asr_enable", False)
        self.assertFalse(self.model.get("conference.upstream.asr_enable"))

    def test_signal_emit(self):
        self.model.load()
        result = {}
        def on_value_changed(path, value):
            result["path"] = path
            result["value"] = value
        self.model.valueChanged.connect(on_value_changed)
        self.model.set("conference.other_lang", "fr")
        self.assertEqual(result["path"], "conference.other_lang")
        self.assertEqual(result["value"], "fr")

if __name__ == "__main__":
    unittest.main()
