import asyncio
from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot
from qasync import asyncSlot
from vpipe.core.capsule import VpState
from ..controller.async_loop_thread import AsyncLoopThread
from pipelines.downstream_pipeline import DownStreamPipeline
from pipelines.selftalk_pipeline import SelfTalkPipeline


class AppState(Enum):
    STOPPED = "Stopped"
    STARTING = "Starting"
    RUNNING = "Running"
    STOPPING = "Stopping"

class ActionState(Enum):
    IDLE = "Idle"
    CHANGING_LANGUAGE = "Changing Language"

class SpeechTranslatorPipeline(QObject):
    appStateChanged = Signal(str)
    actionStateChanged = Signal(str)
    errorChanged = Signal(str)

    def __init__(self, conversation_model, parent=None):
        super().__init__(parent)

        self.conversation_model = conversation_model

        # Async event loop for pipeline
        self._downstream_loop = AsyncLoopThread()
        self._downstream_loop.start()

        self._downstream = SelfTalkPipeline(
            name="selfttalk-pipeline",
            script_writer_callback=self._on_script,
            translated_script_writer_callback=self._on_translated,
        )
        # async def log(msg): print(msg) 
        # self._downstream.bus.add_watch(log)

        # Initial states
        self._app_state = AppState.STOPPED
        self._action_state = ActionState.IDLE
        self._error_message = ""

        # Language settings
        self._other_lang = "en"
        self._your_lang = "vi"

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
        return self._other_lang

    @Property(str)
    def yourLanguage(self):
        return self._your_lang

    # --- Script Callbacks ---
    def _on_script(self, text, is_final):
        if self._current_you_index is not None:
            self.conversation_model.update(self._current_you_index, "Other", text)
            if is_final:
                self._current_you_index = None
        else:
            self.conversation_model.append("Other", text)
            self._current_you_index = None if is_final else self.conversation_model.rowCount() - 1

    def _on_translated(self, text):
        self.conversation_model.append("Other (Translated)", text)

    # --- Control Actions ---
    @asyncSlot()
    async def start(self):
        if self._app_state in (AppState.RUNNING, AppState.STARTING):
            return

        self._set_error("")
        self._set_app_state(AppState.STARTING)
        try:
            await self._downstream_loop.run(self._downstream.set_state(VpState.RUNNING))
            self._set_app_state(AppState.RUNNING)
        except Exception as e:
            self._set_error(f"Start Error: {e}")
            await self._downstream_loop.run(self._downstream.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)

    @asyncSlot()
    async def stop(self):
        if self._app_state in (AppState.STOPPED, AppState.STOPPING):
            return

        self._set_error("")
        self._set_app_state(AppState.STOPPING)
        try:
            await self._downstream_loop.run(self._downstream.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)
        except Exception as e:
            self._set_error(f"Stop Error: {e}")
            await self._downstream_loop.run(self._downstream.set_state(VpState.NULL))
            self._set_app_state(AppState.STOPPED)

    # --- Change Language ---
    @asyncSlot(str)
    async def setOtherLanguage(self, lang):
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        self._other_lang = lang
        try:
            await self._downstream_loop.run(self._downstream.set_prop("src-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
        self._set_action_state(ActionState.IDLE)

    @asyncSlot(str)
    async def setYourLanguage(self, lang):
        self._set_error("")
        self._set_action_state(ActionState.CHANGING_LANGUAGE)
        self._your_lang = lang
        try:
            await self._downstream_loop.run(self._downstream.set_prop("dest-lang", lang))
        except Exception as e:
            self._set_error(f"Language Change Error: {e}")
        self._set_action_state(ActionState.IDLE)

    # --- Adjust Volume ---
    @asyncSlot(float)
    async def setOriginalVolume(self, volume):
        await self._downstream_loop.run(self._downstream.set_prop("src-volume", volume))

    @asyncSlot(float)
    async def setTranslatedVolume(self, volume):
        await self._downstream_loop.run(self._downstream.set_prop("tts-volume", volume))

    # --- Helper ---
    def _code_to_lang(self, code):
        mapping = {
            "en": "English",
            "vi": "Vietnamese",
            "ja": "Japanese"
        }
        return mapping.get(code, code)
