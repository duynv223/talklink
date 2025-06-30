import asyncio
import numpy as np
import sounddevice as sd
from vpipe.core.audiosrc import VpAudioSource
from vpipe.utils.audio_devices import find_device_index


class VpMicSource(VpAudioSource):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name, audio_config=audio_config)
        self.stream = None
        self.device = None
        self._lock = asyncio.Lock()
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
                idx = find_device_index(dev, is_input=True)
                return idx
            except Exception as e:
                return None
        return dev

    async def open(self):
        async with self._lock:
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
        async with self._lock:
            def close():
                if self.stream is not None and getattr(self.stream, 'active', False):
                    self.stream.stop()
                    self.stream.close()
                self.stream = None

            await asyncio.to_thread(close)

    async def read_chunk(self, length):
        async with self._lock:
            def read():
                try:
                    return self.stream.read(length)[0]
                except Exception:
                    return self.silence
            data = await asyncio.to_thread(read)
            return data