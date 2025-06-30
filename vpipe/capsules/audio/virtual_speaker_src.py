import asyncio
import numpy as np
from vpipe.core.audiosrc import VpAudioSource
from vpipe.utils.virtual_audio_device_client import VirtualAudioDeviceClient
from vpipe.utils.cache_resampler import CacheResampler


class VpVirtualSpeakerSrc(VpAudioSource):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name, audio_config=audio_config)

        self.device = None
        self.resampler = CacheResampler(
            sr_in=48000,
            sr_out=self.audio_config.format.rate,
            cache_size=128
        )

    async def open(self):
        def open():
            self.device = VirtualAudioDeviceClient()
            self.resampler.warmup()
        await asyncio.to_thread(open)

    async def close(self):
        def close():
            if self.device:
                self.device.close()
                self.device = None
        await asyncio.to_thread(close)

    async def read_chunk(self, length):
        fmt = self.audio_config.format
        duration = self.audio_config.block_duration

        src_samplerate = 48000
        src_channels = 2
        src_samplewidth = 2

        src_length = int(duration * src_samplerate * src_channels * src_samplewidth)

        try:
            data = await asyncio.to_thread(self.device.read, src_length)
        except Exception:
            data = bytes(src_length)

        if len(data) < src_length:
            data += bytes(src_length - len(data))

        stereo = np.frombuffer(data, dtype=np.int16).reshape(-1, 2)
        mono = stereo.mean(axis=1).astype(np.float32) / 32768.0
        mono = np.clip(mono, -1.0, 1.0)

        out = self.resampler.process(mono)
        out = out.reshape(-1, fmt.channels)
        iinfo = np.iinfo(fmt.dtype)
        out = np.clip(out * iinfo.max, iinfo.min, iinfo.max).astype(fmt.dtype)
        return out
