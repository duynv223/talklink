import numpy as np
import resampy

class CacheResampler:
    def __init__(self, sr_in, sr_out, cache_size, filter='kaiser_best'):
        self.sr_in = sr_in
        self.sr_out = sr_out
        self.cache_size = cache_size
        self.filter = filter
        self.cache = np.zeros(cache_size, dtype=np.float32)

    def warmup(self):
        resampy.resample(np.zeros(1024), sr_orig=self.sr_in, sr_new=self.sr_out)

    def process(self, input_buf: np.ndarray) -> np.ndarray:
        assert input_buf.dtype == np.float32
        padded = np.concatenate([self.cache, input_buf])

        resampled = resampy.resample(
            padded,
            sr_orig=self.sr_in,
            sr_new=self.sr_out,
            filter=self.filter
        )

        skip_start = int((self.cache_size / 2) * self.sr_out / self.sr_in)
        block_frames = int(input_buf.shape[0] * self.sr_out / self.sr_in)
        skip_end = skip_start + block_frames
        resampled = resampled[skip_start:skip_end]

        self.cache = input_buf[-self.cache_size:].copy()
        return resampled
