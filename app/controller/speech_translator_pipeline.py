import asyncio
from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot
from qasync import asyncSlot
from vpipe.core.capsule import VpState
from ..controller.async_loop_thread import AsyncLoopThread
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.selftalk_pipeline import SelfTalkPipeline
from pipelines.dualstream_pipeline import DualStreamPipeline
import logging

logger = logging.getLogger(__name__)

class AppState(Enum):
    STOPPED = "Stopped"
    STARTING = "Starting"
    RUNNING = "Running"
    STOPPING = "Stopping"

class ActionState(Enum):
    IDLE = "Idle"
    CHANGING_LANGUAGE = "Changing Language"
    CHANGING_AUDIO_DEVICE = "Changing Audio Device"
    CHANGING_AUDIO_MUTE = "Changing Audio Mute"

class SpeechTranslatorPipeline(QObject):
    appStateChanged = Signal(str)
    actionStateChanged = Signal(str)
    errorChanged = Signal(str)
    rmsChanged = Signal(str, float)  # stream, rms

    def __init__(self, conversation_model, setting_model, parent=None):
        super().__init__(parent)

        self.conversation_model = conversation_model
        self.setting_model = setting_model
        self.setting_model.valueChanged.connect(self._on_setting_changed)

        self._rms_upstream = 0.0
        self._rms_downstream = 0.0

        # Async event loop for pipeline
        self._loop = AsyncLoopThread()
        self._loop.start()

        self._pipeline = DualStreamPipeline(
            name=".",
            script_writer_callback=self._on_script,
            translated_script_writer_callback=self._on_translated,
            rms_callback=self._on_rms
        )
        
        # Initial states
        self._app_state = AppState.STOPPED
        self._action_state = ActionState.IDLE
        self._error_message = ""

        # UI state
        self._current_you_index = None

    def _on_rms(self, stream, rms):
        if stream == "upstream":
            self._rms_upstream = rms
        elif stream == "downstream":
            self._rms_downstream = rms
        self.rmsChanged.emit(stream, rms)

    # --- State Management ---
    def _set_app_state(self, state: AppState):
        if self._app_state != state:
            logger.info(f"App state changed: {self._app_state.value} -> {state.value}")
            self._app_state = state
            self.appStateChanged.emit(state.value)
            if state == AppState.STOPPED:
                self._rms_upstream = 0.0
                self._rms_downstream = 0.0
                self.rmsChanged.emit("upstream", 0.0)
                self.rmsChanged.emit("downstream", 0.0)

    def _set_action_state(self, state: ActionState):
        if self._action_state != state:
            logger.info(f"Action state changed: {self._action_state.value} -> {state.value}")
            self._action_state = state
            self.actionStateChanged.emit(state.value)

    def _set_error(self, message: str):
        if self._error_message != message:
            logger.error(f"Error: {message}")
            self._error_message = message
            self.errorChanged.emit(message)

    # --- Properties ---
    @Property(str, notify=appStateChanged)
    def appState(self):
        return self._app_state.value

    @Property(str, notify=actionStateChanged)
    def actionState(self):
        return self._action_state.value

    @Property(str, notify=errorChanged)
    def errorMessage(self):
        return self._error_message

    @Property(str)
    def otherLanguage(self):
        return self.setting_model.get("conference.other_lang")

    @Property(str)
    def yourLanguage(self):
        return self.setting_model.get("conference.your_lang")

    @Property('QVariantList', notify=rmsChanged)
    def rms(self):
        return [
            {"stream": "upstream", "rms": self._rms_upstream},
            {"stream": "downstream", "rms": self._rms_downstream}
        ]

    # --- Script Callbacks ---
    def _on_script(self, speaker, text, is_final):
        logger.debug(f"Script received: speaker={speaker}, is_final={is_final}, text={text}")
        if self._current_you_index is not None:
            self.conversation_model.update(self._current_you_index, speaker, text)
            if is_final:
                self._current_you_index = None
        else:
            self.conversation_model.append(speaker, text)
            self._current_you_index = None if is_final else self.conversation_model.rowCount() - 1

    def _on_translated(self, speaker, text):
        logger.debug(f"Translated script: speaker={speaker}, text={text}")
        self.conversation_model.append(f"{speaker} (Translated)", text)

    # --- Control Actions ---
    @asyncSlot()
    async def start(self):
        if self._app_state in (AppState.RUNNING, AppState.STARTING):
            logger.info("Start called but already running or starting.")
            return

        logger.info("Starting pipeline...")
        self._set_error("")
        self._set_app_state(AppState.STARTING)
        try:
            await self._initialize_pipeline_from_settings()
            await self._loop.run(self._pipeline.set_state(VpState.RUNNING))
            self._set_app_state(AppState.RUNNING)
            logger.info("Pipeline started.")
        except Exception as e:
            self._set_error(f"Start Error: {e}")
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)
            logger.exception("Failed to start pipeline.")

    @asyncSlot()
    async def stop(self):
        if self._app_state in (AppState.STOPPED, AppState.STOPPING):
            logger.info("Stop called but already stopped or stopping.")
            return

        logger.info("Stopping pipeline...")
        self._set_error("")
        self._set_app_state(AppState.STOPPING)
        try:
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)
            logger.info("Pipeline stopped.")
        except Exception as e:
            self._set_error(f"Stop Error: {e}")
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)
            logger.exception("Failed to stop pipeline.")

    # --- Change Language ---
    @asyncSlot(str)
    async def set_other_language(self, lang):
        logger.info(f"Changing other language to: {lang}")
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("src-lang", lang))
            await self._loop.run(self._pipeline.upstream.set_prop("dest-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
            logger.exception("Failed to change other language.")
        self._set_action_state(ActionState.IDLE)

    @asyncSlot(str)
    async def set_your_language(self, lang):
        logger.info(f"Changing your language to: {lang}")
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("dest-lang", lang))
            await self._loop.run(self._pipeline.upstream.set_prop("src-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
            logger.exception("Failed to change your language.")
        self._set_action_state(ActionState.IDLE)

    # --- Adjust Volume ---
    @asyncSlot(float)
    async def set_original_volume(self, volume):
        await self._loop.run(self._pipeline.downstream.set_prop("src-volume", volume))
        await self._loop.run(self._pipeline.upstream.set_prop("src-volume", volume))

    @asyncSlot(float)
    async def set_translated_volume(self, volume):
        await self._loop.run(self._pipeline.downstream.set_prop("tts-volume", volume))
        await self._loop.run(self._pipeline.upstream.set_prop("tts-volume", volume))

    # --- Helper ---
    def _code_to_lang(self, code):
        mapping = {
            "en": "English",
            "vi": "Vietnamese",
            "ja": "Japanese"
        }
        return mapping.get(code, code)
    
    @asyncSlot(str, object)
    async def set_asr_enable(self, stream: str, enable: bool):
        match stream:
            case "upstream":
                await self._loop.run(self._pipeline.upstream.set_prop("asr-enable", enable))
            case "downstream":
                await self._loop.run(self._pipeline.downstream.set_prop("asr-enable", enable))
            case _:
                raise ValueError(f"Unknown stream: {stream}")
            
    @asyncSlot(str, object)
    async def set_tts_enable(self, stream: str, enable: bool):
        match stream:
            case "upstream":
                await self._loop.run(self._pipeline.upstream.set_prop("tts-enable", enable))
            case "downstream":
                await self._loop.run(self._pipeline.downstream.set_prop("tts-enable", enable))
            case _:
                raise ValueError(f"Unknown stream: {stream}")
            
    @asyncSlot()
    async def set_input_device(self, device: str):
        self._set_action_state(ActionState.CHANGING_AUDIO_DEVICE)
        try:
            await self._loop.run(self._pipeline.upstream.set_prop("input-device", device))
        except Exception as e:
            self._set_error(f"Audio Device Change Error: {e}")
        finally:
            self._set_action_state(ActionState.IDLE)

    @asyncSlot()
    async def set_output_device(self, device: str):
        self._set_action_state(ActionState.CHANGING_AUDIO_DEVICE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("output-device", device))
        except Exception as e:
            self._set_error(f"Audio Device Change Error: {e}")
        finally:
            self._set_action_state(ActionState.IDLE)

    @asyncSlot()
    async def set_input_audio_mute(self, mute: bool):
        self._set_action_state(ActionState.CHANGING_AUDIO_MUTE)
        try:
            await self._loop.run(self._pipeline.upstream.set_prop("input-mute", mute))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._set_error(f"Audio Mute Change Error: {e}")
        finally:
            self._set_action_state(ActionState.IDLE)

    @asyncSlot()
    async def set_output_audio_mute(self, mute: bool):
        self._set_action_state(ActionState.CHANGING_AUDIO_MUTE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("output-mute", mute))
        except Exception as e:
            self._set_error(f"Audio Mute Change Error: {e}")
        finally:
            self._set_action_state(ActionState.IDLE)

    @asyncSlot()
    async def set_tts_speed(self, stream: str, speed: float):
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        try:
            if stream == "downstream":
                await self._loop.run(self._pipeline.downstream.set_prop("tts-speed", speed))
            elif stream == "upstream":
                await self._loop.run(self._pipeline.upstream.set_prop("tts-speed", speed))
            else:
                raise ValueError(f"Unknown stream: {stream}")
        except Exception as e:
            self._set_error(f"TTS Speed Change Error: {e}")
        finally:
            self._set_action_state(ActionState.IDLE)

            
    @asyncSlot(str, object)
    async def _initialize_pipeline_from_settings(self):
        await self.set_your_language(self.setting_model.get("conference.your_lang"))
        await self.set_other_language(self.setting_model.get("conference.other_lang"))
        await self.set_original_volume(self.setting_model.get("conference.volume.original"))
        await self.set_translated_volume(self.setting_model.get("conference.volume.translated"))
        await self.set_asr_enable("downstream", self.setting_model.get("conference.downstream.asr_enable"))
        await self.set_tts_enable("downstream", self.setting_model.get("conference.downstream.tts_enable"))
        await self.set_asr_enable("upstream", self.setting_model.get("conference.upstream.asr_enable"))
        await self.set_tts_enable("upstream", self.setting_model.get("conference.upstream.tts_enable"))
        await self.set_input_device(self.setting_model.get("conference.input_device"))
        await self.set_output_device(self.setting_model.get("conference.output_device"))
        await self.set_input_audio_mute(self.setting_model.get("conference.input_mute"))
        await self.set_output_audio_mute(self.setting_model.get("conference.output_mute"))
        await self.set_tts_speed("downstream", self.setting_model.get("conference.downstream.tts_speed"))
        await self.set_tts_speed("upstream", self.setting_model.get("conference.upstream.tts_speed"))

    @asyncSlot(str, object)
    async def _on_setting_changed(self, path, value):
        match path:
            # langeage settings
            case "conference.your_lang":
                await self.set_your_language(value)
            case "conference.other_lang":
                await self.set_other_language(value)
            # volume settings
            case "conference.volume.original":
                await self.set_original_volume(value)
            case "conference.volume.translated":
                await self.set_translated_volume(value)
            # ASR and TTS settings
            case "conference.downstream.asr_enable":
                await self.set_asr_enable("downstream", value)
            case "conference.downstream.tts_enable":
                await self.set_tts_enable("downstream", value)
            case "conference.upstream.asr_enable":
                await self.set_asr_enable("upstream", value)
            case "conference.upstream.tts_enable":
                await self.set_tts_enable("upstream", value)
            # Audio device settings
            case "conference.input_device":
                await self.set_input_device(value)
            case "conference.output_device":
                await self.set_output_device(value)
            # Audio mute
            case "conference.input_mute":
                await self.set_input_audio_mute(value)
            case "conference.output_mute":
                await self.set_output_audio_mute(value)
            # TTS playback speed
            case "conference.downstream.tts_speed":
                await self.set_tts_speed("downstream", value)
            case "conference.upstream.tts_speed":
                await self.set_tts_speed("upstream", value)
            # Unhandled settings
            case _:
                logger.warning(f"Unhandled setting change: {path} = {value}")
