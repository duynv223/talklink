import asyncio

from vpipe.core.transform import VpBaseTransform
from vpipe.core.pipeline import VpPipeline

from vpipe.capsules.audio.virtual_mic_sink import VirtualMicSink
from vpipe.capsules.audio.mic_source import VpMicSource
from pipelines.augmented_speech_translator import AugmentedSpeechTranslator


class ScriptWriter(VpBaseTransform):
    def __init__(self, name="script-writer", handler=None):
        super().__init__(name)
        self.handler = handler

    async def transform(self, data):
        if self.handler and data:
            text, is_final = data
            self.handler(text, is_final)
        await asyncio.sleep(0)


class TranslatedScriptWriter(VpBaseTransform):
    def __init__(self, name="translated-script-writer", handler=None):
        super().__init__(name)
        self.handler = handler

    async def transform(self, data):
        if self.handler and data:
            self.handler(data)
        await asyncio.sleep(0)


class UpStreamPipeline(VpPipeline):
    """
    (Mic source) → [augmented speech translator] → (virtual mic sink)
    """
    def __init__(self,
                 name="downstream-pipeline",
                 script_writer_callback=None,
                 translated_script_writer_callback=None):
        
        super().__init__(name)
        self.script_writer_callback = script_writer_callback
        self.translated_script_writer_callback = translated_script_writer_callback
        self.build()

    def build(self):
        src = VpMicSource(name="mic-src")
        sink = VirtualMicSink(name="virtual-mic-sink")
        translator = AugmentedSpeechTranslator(name="augmented-speech-translator",
                                               src_lang='vi', dest_lang='en')
        src >> translator >> sink

        script_writer = ScriptWriter(name="script-writer",
                                    handler=self.script_writer_callback)
        
        translated_script_writer = TranslatedScriptWriter(name="translated-script-writer",
                                    handler=self.translated_script_writer_callback)
        
        translator.get_output("asr_script") >> script_writer
        translator.get_output("tran_script") >> translated_script_writer

        self.adds(
            src,
            sink,
            translator,
        )
    
    async def set_prop(self, prop, value):
        match prop:
            case 'src-lang' | 'dest-lang' | 'src-volume' | 'tts-volume':
                await self.get_capsule("augmented-speech-translator").set_prop(prop, value)
            case _:
                raise ValueError(f"Unknown property: {prop}")