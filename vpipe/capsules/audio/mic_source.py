import asyncio
import numpy as np
import sounddevice as sd
from vpipe.core.audiosrc import VpAudioSource
from vpipe.core.config import GLOBAL_AUDIO_CONFIG


class VpMicSource(VpAudioSource):
    def __init__(self, samplewidth=2, audio_config=None):
        super().__init__(audio_config=audio_config or GLOBAL_AUDIO_CONFIG)
        self.stream = None
        self.silence = np.zeros((self.audio_config.blocksize,
                                  self.audio_config.format.channels),
                                 dtype=self.audio_config.format.dtype)

    async def open(self):
        def start():
            fmt = self.audio_config.format

            self.stream = sd.InputStream(
                samplerate=fmt.rate,
                channels=fmt.channels,
                blocksize=self.audio_config.blocksize,
                dtype=fmt.dtype
            )
            self.stream.start()
        await asyncio.to_thread(start)

    async def close(self):
        def stop():
            if self.stream is not None and self.stream.active:
                self.stream.stop()
                self.stream.close()
                self.stream = None

        await asyncio.to_thread(stop)

    async def read_chunk(self, length):
        def read():
            try:
                return self.stream.read(length)[0]
            except Exception as e:
                return self.silence
        
        data = await asyncio.to_thread(read)
        return data