import numpy as np
from vpipe.core.transform import VpBaseTransform

class VpVolume(VpBaseTransform):
    def __init__(self, name=None, volume: float = 1.0):
        super().__init__(name=name)
        self.volume = volume
        self.mute = False

    async def set_prop(self, prop, value):
        if prop == 'volume':
            self.volume = value
        elif prop == 'mute':
            self.mute = value
        else:
            raise ValueError(f"Unknown property: {prop}")

    async def transform(self, data):
        if self.mute:            
            return np.zeros_like(data)
        else:
            return (data * self.volume).astype(data.dtype)

    def set_level(self, volume: float):
        """
        Deprecated: Use set_prop('volume', value) instead.
        """
        self.volume = volume