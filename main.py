import os
import sys
import asyncio
import logging
import logging.config
from queue import Queue
import yaml
from pathlib import Path
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from app.models.conversation_model import ConversationModel
from app.models.setting_model import SettingModel
from app.models.service_setting_model import ServiceSettingModel
from app.controller.speech_translator_pipeline import SpeechTranslatorPipeline
from app.utils.qml_utils import init_engine, set_window_title
from app.models.audio_device_manager import AudioDeviceManager
from services.service_manager import ServiceManager

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"


def init_logging():
    config_path = Path(__file__).resolve().parent / "logging.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)


async def main():
    init_logging()
    ServiceManager(config_path='services/services_config.yaml',
                   settings_path='service_setting.yaml')

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    audio_device_manager = AudioDeviceManager()
    conversation_model = ConversationModel()
    setting_model = SettingModel('setting.yaml')
    setting_model.load()

    pipeline = SpeechTranslatorPipeline(
        conversation_model=conversation_model,
        setting_model=setting_model
    )

    service_setting_model = ServiceSettingModel(
        str(Path(__file__).resolve().parent / "services" / "services_config.yaml"),
        str(Path(__file__).resolve().parent / "service_setting.yaml")
    )

    service_setting_model.serviceChanged.connect(lambda *_: ServiceManager().reload_settings())
    service_setting_model.fieldChanged.connect(lambda *_: ServiceManager().reload_settings())

    qml_path = Path(__file__).resolve().parent / "app" / "qml" / "main.qml"
    qml_engine = init_engine(qml_path, {
        "pipeline": pipeline,
        "conversationModel": conversation_model,
        "settingModel": setting_model,
        "audioDeviceManager": audio_device_manager,
        "serviceSettingModel": service_setting_model
    })

    if not qml_engine.rootObjects():
        print("Failed to load QML file.")
        sys.exit(-1)

    root = qml_engine.rootObjects()[0]
    set_window_title(root, "Speech Translator (Self Talk mode for development)")

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
