import asyncio
import sounddevice as sd
from vpipe.core.audiosink import VpAudioSink
from vpipe.core.config import GLOBAL_AUDIO_CONFIG


class VpSpeakerSink(VpAudioSink):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name, audio_config=audio_config or GLOBAL_AUDIO_CONFIG)

        fmt = self.audio_config.format

        self.stream = sd.OutputStream(
            samplerate=fmt.rate,
            channels=fmt.channels,
            blocksize=self.audio_config.blocksize,
            dtype=fmt.dtype
        )
    
    async def open(self):
        if not self.stream.active:
            self.stream.start()
    
    async def close(self):
        if self.stream.active:
            self.stream.stop()

    async def write(self, buf):
        await asyncio.to_thread(self.stream.write, buf)
