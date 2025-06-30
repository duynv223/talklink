import time
import numpy as np
import asyncio
from vpipe.core.audiosink import VpAudioSink
from vpipe.utils.virtual_audio_device_client import VirtualAudioDeviceClient
from vpipe.utils.cache_resampler import CacheResampler


class VirtualMicSink(VpAudioSink):
    def __init__(self, name=None, audio_config=None):
        super().__init__(audio_config=audio_config)
        self._name = name or "virtual-mic-sink"
        self.device = None
        self.resampler = CacheResampler(sr_in=16000, sr_out=48000, cache_size=128)

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

    async def write(self, buf):
        """
        buf: (2048,1), int16 mono 16kHz
        dev: int32 PCM stereo, 48kHz
        """
        # resample from 16kHz to 48kHz
        mono = buf.reshape(-1).astype(np.float32) / 32768.0
        resampled = self.resampler.process(mono)
        stereo = np.stack([resampled, resampled], axis=-1)

        # Convert to int32 PCM
        pcm_int32 = np.clip(
            stereo * (2**31 - 1),
            -(2**31),
            (2**31 - 1)
        ).astype(np.int32)

        # Split into 10ms chunks
        total_frames = pcm_int32.shape[0]
        chunk_frames = 480 # ~10ms at 48kHz
        chunks = []
        for start in range(0, total_frames, chunk_frames):
            end = min(start + chunk_frames, total_frames)
            chunk_bytes = pcm_int32[start:end].tobytes()
            chunks.append(chunk_bytes)

        # Write each chunk
        def write_chunks():
            chunk_iter = iter(chunks)
            while True:
                try:
                    next_chunk = next(chunk_iter)
                except StopIteration:
                    break
                while True:
                    used, free = self.device.get_mic_status()
                    if free >= len(next_chunk):
                        self.device.write(next_chunk)
                        break
                    else:
                        time.sleep(0.003)
        await asyncio.to_thread(write_chunks)
