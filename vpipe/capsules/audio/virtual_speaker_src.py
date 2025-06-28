import numpy as np
import resampy
import asyncio
from vpipe.core.audiosrc import VpAudioSource
from .vadc import VirtualAudioDeviceClient
from vpipe.core.config import GLOBAL_AUDIO_CONFIG, AudioFormat


class StreamingResampler:
    def __init__(self, sr_in: int, sr_out: int, cache_samples: int = 128):
        self.sr_in = sr_in
        self.sr_out = sr_out
        self.cache = np.zeros(cache_samples, dtype=np.float32)
        self.cache_samples = cache_samples

    def warmup(self):
        resampy.resample(np.zeros(1024), sr_orig=self.sr_in, sr_new=self.sr_out)

    def process(self, mono: np.ndarray) -> np.ndarray:
        padded = np.concatenate([self.cache, mono])

        resampled = resampy.resample(
            padded,
            sr_orig=self.sr_in,
            sr_new=self.sr_out,
            filter='kaiser_best'
        )

        skip = int(self.cache_samples * self.sr_out / self.sr_in)
        if skip > 0:
            resampled = resampled[skip//2:-skip//2]

        self.cache = mono[-self.cache_samples:].copy()

        resampled *= 0.99
        return np.clip(resampled * 32767, -32768, 32767).astype(np.int16)


class VpVirtualSpeakerSrc(VpAudioSource):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name, audio_config=audio_config or GLOBAL_AUDIO_CONFIG)

        self.device = None
        self.resampler = StreamingResampler(
            sr_in=48000,
            sr_out=self.audio_config.format.rate,
            cache_samples=256
        )

    async def open(self):
        self.device = VirtualAudioDeviceClient()
        self.resampler.warmup()

    async def close(self):
        self.device.close()

    async def read_chunk(self, length):
        fmt = self.audio_config.format
        blocksize = self.audio_config.blocksize
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
        return out.reshape(blocksize, fmt.channels).astype(fmt.dtype)
