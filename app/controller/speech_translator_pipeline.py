import asyncio
from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot
from qasync import asyncSlot
from vpipe.core.capsule import VpState
from ..controller.async_loop_thread import AsyncLoopThread
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.selftalk_pipeline import SelfTalkPipeline
from pipelines.dualstream_pipeline import DualStreamPipeline


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

    def __init__(self, conversation_model, setting_model, parent=None):
        super().__init__(parent)

        self.conversation_model = conversation_model
        self.setting_model = setting_model
        self.setting_model.valueChanged.connect(self._on_setting_changed)

        # Async event loop for pipeline
        self._loop = AsyncLoopThread()
        self._loop.start()

        self._pipeline = DualStreamPipeline(
            name="downstream-pipeline",
            script_writer_callback=self._on_script,
            translated_script_writer_callback=self._on_translated,
        )
        
        # Initial states
        self._app_state = AppState.STOPPED
        self._action_state = ActionState.IDLE
        self._error_message = ""

        # UI state
        self._current_you_index = None

    # --- State Management ---
    def _set_app_state(self, state: AppState):
        if self._app_state != state:
            self._app_state = state
            self.appStateChanged.emit(state.value)

    def _set_action_state(self, state: ActionState):
        if self._action_state != state:
            self._action_state = state
            self.actionStateChanged.emit(state.value)

    def _set_error(self, message: str):
        if self._error_message != message:
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
        print("Other Language:", self.setting_model.get("conference.other_lang"))
        return self.setting_model.get("conference.other_lang")

    @Property(str)
    def yourLanguage(self):
        return self.setting_model.get("conference.your_lang")

    # --- Script Callbacks ---
    def _on_script(self, speaker, text, is_final):
        if self._current_you_index is not None:
            self.conversation_model.update(self._current_you_index, speaker, text)
            if is_final:
                self._current_you_index = None
        else:
            self.conversation_model.append(speaker, text)
            self._current_you_index = None if is_final else self.conversation_model.rowCount() - 1

    def _on_translated(self, speaker, text):
        self.conversation_model.append(f"{speaker} (Translated)", text)

    # --- Control Actions ---
    @asyncSlot()
    async def start(self):
        if self._app_state in (AppState.RUNNING, AppState.STARTING):
            return

        self._set_error("")
        self._set_app_state(AppState.STARTING)
        try:
            await self._initialize_pipeline_from_settings()
            await self._loop.run(self._pipeline.set_state(VpState.RUNNING))
            self._set_app_state(AppState.RUNNING)
        except Exception as e:
            self._set_error(f"Start Error: {e}")
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)

    @asyncSlot()
    async def stop(self):
        if self._app_state in (AppState.STOPPED, AppState.STOPPING):
            return

        self._set_error("")
        self._set_app_state(AppState.STOPPING)
        try:
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)
        except Exception as e:
            self._set_error(f"Stop Error: {e}")
            await self._loop.run(self._pipeline.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)

    # --- Change Language ---
    @asyncSlot(str)
    async def setOtherLanguage(self, lang):
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("src-lang", lang))
            await self._loop.run(self._pipeline.upstream.set_prop("dest-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
        self._set_action_state(ActionState.IDLE)

    @asyncSlot(str)
    async def setYourLanguage(self, lang):
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        try:
            await self._loop.run(self._pipeline.downstream.set_prop("dest-lang", lang))
            await self._loop.run(self._pipeline.upstream.set_prop("src-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
        self._set_action_state(ActionState.IDLE)

    # --- Adjust Volume ---
    @asyncSlot(float)
    async def setOriginalVolume(self, volume):
        await self._loop.run(self._pipeline.downstream.set_prop("src-volume", volume))
        await self._loop.run(self._pipeline.upstream.set_prop("src-volume", volume))

    @asyncSlot(float)
    async def setTranslatedVolume(self, volume):
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
        await self.setYourLanguage(self.setting_model.get("conference.your_lang"))
        await self.setOtherLanguage(self.setting_model.get("conference.other_lang"))
        await self.setOriginalVolume(self.setting_model.get("conference.volume.original"))
        await self.setTranslatedVolume(self.setting_model.get("conference.volume.translated"))
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
                await self.setYourLanguage(value)
            case "conference.other_lang":
                await self.setOtherLanguage(value)
            # volume settings
            case "conference.volume.original":
                await self.setOriginalVolume(value)
            case "conference.volume.translated":
                await self.setTranslatedVolume(value)
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
                print(f"Unhandled setting change: {path} = {value}")
