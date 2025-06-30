import asyncio
import sounddevice as sd
from vpipe.core.audiosink import VpAudioSink
from vpipe.utils.audio_devices import find_device_index


class VpSpeakerSink(VpAudioSink):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name, audio_config=audio_config)
        self.stream = None
        self.device = None
        self._lock = asyncio.Lock()

    async def _set_device(self, device: str):
        self.device = device
        if self.stream and getattr(self.stream, 'active', False):
            await self.close()
            await self.open()

    def _resolve_device(self, dev):
        if isinstance(dev, str):
            idx = find_device_index(dev, is_input=False)
            return idx
        return dev

    async def set_prop(self, key: str, value):
        match key:
            case 'device':
                await self._set_device(value)
            case _:
                raise ValueError(f"Unknown property: {key}")

    async def open(self):
        async with self._lock:
            fmt = self.audio_config.format
            device_index = self._resolve_device(self.device)
            self.stream = sd.OutputStream(
                samplerate=fmt.rate,
                channels=fmt.channels,
                blocksize=self.audio_config.blocksize,
                dtype=fmt.dtype,
                device=device_index
            )
            await asyncio.to_thread(self.stream.start)

    async def close(self):
        async with self._lock:
            if self.stream:
                if getattr(self.stream, 'active', False):
                    await asyncio.to_thread(self.stream.stop)
                    await asyncio.to_thread(self.stream.close)
                self.stream = None

    async def write(self, buf):
        async with self._lock:
            if self.stream and getattr(self.stream, 'active', False):
                await asyncio.to_thread(self.stream.write, buf)
