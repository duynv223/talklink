from vpipe.core.composite import VpComposite
from vpipe.core.queue import VpQueue, DrainPolicy
from vpipe.core.capsule import VpState
from vpipe.core.transform import VpBaseTransform
from vpipe.capsules.services.asr import ASRTransform
from vpipe.capsules.services.tts import TTSTransform
from vpipe.capsules.services.tran import TranslationTransform
from services.service_manager import ServiceManager


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
                 src_lang='en',
                 dest_lang='vi'):
        
        super().__init__(name)
        self._src_lang = src_lang
        self._dest_lang = dest_lang
        self.build()

    def build(self):
        def asr_service_factory(lang='en'):
            sm = ServiceManager()
            sel_id = sm.get_selected_service_id('ASR')
            service_cls = sm.get_service_class('ASR', sel_id)
            settings = sm.get_service_settings('ASR', sel_id)
            return service_cls(lang=lang, settings=settings)

        def tts_service_factory():
            sm = ServiceManager()
            sel_id = sm.get_selected_service_id('TTS')
            service_cls = sm.get_service_class('TTS', sel_id)
            settings = sm.get_service_settings('TTS', sel_id)
            return service_cls(settings=settings)

        def tran_service_factory():
            sm = ServiceManager()
            sel_id = sm.get_selected_service_id('TRA')
            service_cls = sm.get_service_class('TRA', sel_id)
            settings = sm.get_service_settings('TRA', sel_id)
            return service_cls(settings=settings)
        
        # ASR
        q1 = VpQueue(name='q1', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        asr_transform = ASRTransform('asr', service_factory=asr_service_factory, lang=self._src_lang)
        text_complete_filter = TextCompleteFilter()

        # Translation
        q2 = VpQueue(name='q2', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        tran_transform = TranslationTransform('tran', service_factory=tran_service_factory,
                                              src=self._src_lang, dest=self._dest_lang)

        # TTS
        q3 = VpQueue(name='q3', maxsize=10, leaky=DrainPolicy.DOWNSTREAM)
        tts_transform = TTSTransform('tts', service_factory=tts_service_factory,
                                     lang=self._dest_lang)

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
                await asr.set_prop("enable", value)
            case "tts-enable":
                tts = self.get_capsule("tts")
                await tts.set_prop("enable", value)
            case _:
                raise ValueError(f"Unknown property: {prop}")

    async def _set_src_lang(self, src_lang):
        self._src_lang = src_lang
        
        # ASR
        asr = self.get_capsule("asr")
        await asr.set_prop("lang", src_lang)

        # Translation
        tran = self.get_capsule("tran")
        await tran.set_prop("src-lang", src_lang)
    
    async def _set_dest_lang(self, dest_lang):
        self._dest_lang = dest_lang

        # Translation
        tran = self.get_capsule("tran")
        await tran.set_prop("dest-lang", dest_lang)

        # TTS
        tts = self.get_capsule("tts")
        await tts.set_prop("lang", dest_lang)

