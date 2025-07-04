import asyncio

from vpipe.core.transform import VpBaseTransform
from vpipe.core.pipeline import VpPipeline
from vpipe.core.queue import VpQueue, DrainPolicy

from vpipe.capsules.audio.virtual_mic_sink import VirtualMicSink
from vpipe.capsules.audio.mic_source import VpMicSource
from vpipe.capsules.audio.volume import VpVolume
from pipelines.augmented_speech_translator import AugmentedSpeechTranslator
from vpipe.capsules.audio.rms_transform import VpRmsTransform
from vpipe.capsules.services.payload import Payload

class ScriptWriter(VpBaseTransform):
    def __init__(self, name="script-writer", handler=None):
        super().__init__(name)
        self.handler = handler

    async def transform(self, data: Payload):
        if self.handler and data:
            self.handler(data)
        await asyncio.sleep(0)


class TranslatedScriptWriter(VpBaseTransform):
    def __init__(self, name="translated-script-writer", handler=None):
        super().__init__(name)
        self.handler = handler

    async def transform(self, data: Payload):
        if self.handler and data:
            self.handler(data)
        await asyncio.sleep(0)


class UpStreamPipeline(VpPipeline):
    """
    (Mic source) → [augmented speech translator] → (virtual mic sink)
    """
    def __init__(self,
                 name="upstream-pipeline",
                 script_writer_callback=None,
                 translated_script_writer_callback=None,
                 rms_callback=lambda data: None):
        
        super().__init__(name)
        self.script_writer_callback = script_writer_callback
        self.translated_script_writer_callback = translated_script_writer_callback
        self.rms_callback = rms_callback
        self.build()

    def build(self):
        src = VpMicSource(name="mic-src")
        q1 = VpQueue(name='q1', maxsize=2, leaky=DrainPolicy.DOWNSTREAM)
        sink = VirtualMicSink(name="virtual-mic-sink")
        volume = VpVolume(name="volume-control")
        translator = AugmentedSpeechTranslator(name="ast",
                                               src_lang='vi', dest_lang='en')
        rms_transform = VpRmsTransform(name="rms-transform")

        src >> volume >> translator >> q1 >> sink
        src >> rms_transform

        script_writer = ScriptWriter(name="script-writer",
                                    handler=self.script_writer_callback)
        
        translated_script_writer = TranslatedScriptWriter(name="translated-script-writer",
                                    handler=self.translated_script_writer_callback)
        
        translator.get_output("asr_script") >> script_writer
        translator.get_output("tran_script") >> translated_script_writer
        async def on_rms_callback(name, data): self.rms_callback(data)
        rms_transform.out.set_chain_callback(on_rms_callback)

        self.adds(
            src,
            q1,
            sink,
            translator,
            volume,
            rms_transform,
            script_writer,
            translated_script_writer
        )
    
    async def set_prop(self, prop, value):
        match prop:
            case 'src-lang' | 'dest-lang' | 'src-volume' | 'tts-volume' | 'asr-enable' | 'tts-enable' | 'tts-speed':
                await self.get_capsule("ast").set_prop(prop, value)
            case 'input-device':
                src = self.get_capsule("mic-src")
                await src.set_prop("device", value)
            case 'input-mute':
                volume = self.get_capsule("volume-control")
                await volume.set_prop("mute", value)
            case _:
                raise ValueError(f"Unknown property: {prop}")