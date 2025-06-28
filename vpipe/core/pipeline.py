import asyncio
from vpipe.core.composite import VpComposite
from vpipe.core.bus import VpBus


class VpPipeline(VpComposite):
    def __init__(self, name=None):
        super().__init__(name)
        self.bus = VpBus(name + "-bus" if name else None)
