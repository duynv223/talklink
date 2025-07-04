import asyncio

from vpipe.core.transform import VpBaseTransform
from vpipe.core.pipeline import VpPipeline
from vpipe.core.queue import VpQueue, DrainPolicy

from vpipe.capsules.audio.speaker_sink import VpSpeakerSink
from vpipe.capsules.audio.virtual_speaker_src import VpVirtualSpeakerSrc
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


class DownStreamPipeline(VpPipeline):
    """
    (virtual speaker source) → [augmented speech translator] → (speaker sink)
    """
    def __init__(self,
                 name="downstream-pipeline",
                 script_writer_callback=None,
                 translated_script_writer_callback=None,
                 rms_callback=lambda data: None):
        
        super().__init__(name)
        self.script_writer_callback = script_writer_callback
        self.translated_script_writer_callback = translated_script_writer_callback
        self.rms_callback = rms_callback
        self.build()

    def build(self):
        src = VpVirtualSpeakerSrc(name="virtual-speaker-src")
        q1 = VpQueue(name='q1', maxsize=2, leaky=DrainPolicy.DOWNSTREAM)
        sink = VpSpeakerSink(name="speaker-sink")
        volume = VpVolume(name="volume-control")
        
        translator = AugmentedSpeechTranslator(name="ast",
                                               src_lang='en', dest_lang='vi')
        rms_transform = VpRmsTransform(name="rms-transform")

        src >> translator >> volume >> q1 >> sink
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
            case 'output-device':
                sink = self.get_capsule("speaker-sink")
                await sink.set_prop("device", value)
            case 'output-mute':
                volume = self.get_capsule("volume-control")
                await volume.set_prop("mute", value)
            case _:
                raise ValueError(f"Unknown property: {prop}")