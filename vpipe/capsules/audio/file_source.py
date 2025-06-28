import asyncio
from pydub import AudioSegment
import numpy as np
from vpipe.core.audiosrc import VpAudioSource
from vpipe.core.config import GLOBAL_AUDIO_CONFIG, AudioConfig


class VpFileSource(VpAudioSource):
    def __init__(self, filepath: str, audio_config: AudioConfig = None):
        super().__init__(audio_config=audio_config or GLOBAL_AUDIO_CONFIG)
        self.filepath = filepath
        self.samples = None
        self.position = 0

    async def open(self):
        fmt = self.audio_config.format

        audio = AudioSegment.from_file(self.filepath) \
            .set_channels(fmt.channels) \
            .set_sample_width(fmt.dtype().itemsize) \
            .set_frame_rate(fmt.rate)

        samples = np.frombuffer(audio.raw_data, dtype=fmt.dtype)
        self.samples = samples.reshape((-1, fmt.channels))
        self.position = 0

    async def close(self):
        self.audio = None
        self.samples = None
        self.position = 0

    async def read_chunk(self, length):
        if self.samples is None or self.position >= len(self.samples):
            return None

        end = self.position + length
        chunk = self.samples[self.position:end]
        self.position = end

        return chunk.copy()
