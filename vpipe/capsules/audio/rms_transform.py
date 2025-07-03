import numpy as np
from vpipe.core.transform import VpBaseTransform
from vpipe.core.config import AudioFormat

class VpRmsTransform(VpBaseTransform):
    """
    Transform that receives a numpy audio array of shape (n_samples, channels)
    and returns the mean RMS value across channels, normalized to 0-1.
    """
    def __init__(self, name=None, audio_format: AudioFormat = None):
        super().__init__(name=name)
        self.audio_format = audio_format or AudioFormat()

    async def transform(self, data):
        # data: numpy array, shape (n_samples, channels)
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=self.audio_format.dtype)
        if data.ndim != 2:
            raise ValueError("VpRmsTransform only supports 2D arrays with shape (n_samples, channels)")

        rms = np.sqrt(np.mean(np.square(data.astype(np.float32)), axis=0)).mean()
        dtype = self.audio_format.dtype
        max_val = np.iinfo(dtype).max
        normalized_rms = float(rms) / max_val if max_val else 0.0
        return min(max(normalized_rms, 0.0), 1.0)
