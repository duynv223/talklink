from vpipe.core.composite import VpComposite
from vpipe.core.queue import VpQueue, DrainPolicy
from vpipe.core.capsule import VpState
from vpipe.core.transform import VpBaseTransform
from vpipe.capsules.services.asr import ASRTransform
from vpipe.capsules.services.tts import TTSTransform
from vpipe.capsules.services.tran import TranslationTransform

from services.google_translator_service import GoogleTranslatorService
from services.google_tts_service import GoogleTTSService
from services.deepgram_asr_service import DeepGramASRService
from services.whisper_asr_service import WhisperASRService


class TextCompleteFilter(VpBaseTransform):
    async def transform(self, data):
        if data:
            text, is_final = data
            return text if is_final else None


class SpeechTranslator(VpComposite):
    """
    Pipeline:
        (in) → q1 → asr_transform → q2 → tran_transform → q3 → tts_transform → (out) 
                                  → (asr_script)        → (tran_script)
    """

    def __init__(self, name=None,
                 asr_service_cls=DeepGramASRService, #WhisperASRService or DeepGramASRService
                 tts_service_cls=GoogleTTSService,
                 tran_service_cls=GoogleTranslatorService,
                 src_lang='en',
                 dest_lang='vi'):
        
        super().__init__(name)
        self._asr_service_cls = asr_service_cls
        self._tts_service_cls = tts_service_cls
        self._tran_service_cls = tran_service_cls
        self._src_lang = src_lang
        self._dest_lang = dest_lang
        self.build()

    def build(self):
        # Create services
        asr_service = self._asr_service_cls(lang=self._src_lang)
        tts_service = self._tts_service_cls()
        tran_service = self._tran_service_cls()

        # ASR
        q1 = VpQueue(name='q1', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        asr_transform = ASRTransform('asr', service=asr_service)
        text_complete_filter = TextCompleteFilter()

        # Translation
        q2 = VpQueue(name='q2', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        tran_transform = TranslationTransform('tran', service=tran_service,
                                              src=self._src_lang, dest=self._dest_lang)

        # TTS
        q3 = VpQueue(name='q3', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        tts_transform = TTSTransform('tts', service=tts_service, lang=self._dest_lang)

        # Add capsules
        self.adds(
            q1, asr_transform, text_complete_filter,
            q2, tran_transform,
            q3, tts_transform
        )

        # Connect capsules
        q1 >> asr_transform >> text_complete_filter >> q2 >> tran_transform >> q3 >> tts_transform

        # Expose inputs and outputs
        self.expose_input("in", q1.get_input("in"))
        self.expose_output("out", tts_transform.get_output("out"))
        self.expose_output("asr_script", asr_transform.get_output("out"))
        self.expose_output("tran_script", tran_transform.get_output("out"))

    async def set_prop(self, prop, value):
        match prop:
            case "src-lang":
                await self._set_src_lang(value)
            case "dest-lang":
                await self._set_dest_lang(value)
            case "asr-enable":
                asr = self.get_capsule("asr")
                asr.set_prop("enable", value)
            case "tts-enable":
                tts = self.get_capsule("tts")
                tts.set_prop("enable", value)
            case _:
                raise ValueError(f"Unknown property: {prop}")

    async def _set_src_lang(self, src_lang):
        """
        ASR: Reload ASR service with new source language.
        Translation: No need to reload, as it can handle multiple languages dynamically.
        TTS: Don't care
        """
        self._src_lang = src_lang

        # Reaload ASR with new languages
        asr_service = self._asr_service_cls(lang=self._src_lang)

        queue = self.get_capsule("q1")
        asr = self.get_capsule("asr")
        
        state = self.state
        if state == VpState.RUNNING:
            await queue.set_state(VpState.PAUSED)
        
        if state in (VpState.PAUSED, VpState.RUNNING):
            await asr.set_state(VpState.READY)

        asr.set_service(asr_service)
        await queue.flush()
        await queue.set_state(state)
        await asr.set_state(state)

        # Translation
        tran = self.get_capsule("tran")
        tran.set_prop("src-lang", self._src_lang)
    
    async def _set_dest_lang(self, dest_lang):
        """
        ASR: Don't care
        Translation: No need to reload, as it can handle multiple languages dynamically.
        TTS: No need to reload, as it can handle multiple languages dynamically.
        """
        self._dest_lang = dest_lang

        # Translation
        tran = self.get_capsule("tran")
        tran.set_prop("dest-lang", self._dest_lang)

        # TTS
        tts = self.get_capsule("tts")
        tts.set_prop("lang", self._dest_lang)

