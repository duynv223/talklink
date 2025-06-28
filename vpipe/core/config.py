from dataclasses import dataclass
import numpy as np
from typing import Literal


@dataclass
class AudioFormat:
    rate: int = 16000
    channels: int = 1
    dtype: type = np.int16

    @property
    def sample_size(self) -> int:
        return self.dtype().itemsize


@dataclass
class AudioConfig:
    format: AudioFormat
    blocksize: int = 4096

    @property
    def block_duration(self) -> float:
        return self.blocksize / self.format.rate


GLOBAL_AUDIO_CONFIG = AudioConfig(
    format=AudioFormat(rate=16000, channels=1, dtype=np.int16),
    blocksize=2048
)
