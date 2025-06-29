import asyncio
import numpy as np
import sounddevice as sd
from vpipe.core.audiosrc import VpAudioSource
from vpipe.utils.audio_devices import find_device_index


class VpMicSource(VpAudioSource):
    def __init__(self, name=None, samplewidth=2, audio_config=None):
        super().__init__(name=name, audio_config=audio_config)
        self.stream = None
        self.device = None
        self.silence = np.zeros((self.audio_config.blocksize,
                                  self.audio_config.format.channels),
                                 dtype=self.audio_config.format.dtype)
        
    async def set_prop(self, key: str, value):
        match key:
            case 'device':
                await self._set_device(value)
            case _:
                raise ValueError(f"Unknown property: {key}")
            
    async def _set_device(self, device: str):
        self.device = device
        if self.stream is not None and getattr(self.stream, 'active', False):
            await self.close()
            await self.open()

    def _resolve_device(self, dev):
        if isinstance(dev, str):
            try:
                return find_device_index(dev, is_input=True)
            except Exception:
                return None
        return dev

    async def open(self):
        def start():
            fmt = self.audio_config.format
            device_index = self._resolve_device(self.device)

            self.stream = sd.InputStream(
                samplerate=fmt.rate,
                channels=fmt.channels,
                blocksize=self.audio_config.blocksize,
                dtype=fmt.dtype,
                device=device_index
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