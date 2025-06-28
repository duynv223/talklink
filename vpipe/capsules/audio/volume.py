from vpipe.core.transform import VpBaseTransform

class VpVolume(VpBaseTransform):
    def __init__(self, volume: float = 1.0):
        super().__init__()
        self.volume = volume

    async def transform(self, data):
        return (data * self.volume).astype(data.dtype)

    def set_level(self, volume: float):
        self.volume = volume