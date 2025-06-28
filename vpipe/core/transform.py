import asyncio
from .capsule import VpCapsule

class VpBaseTransform(VpCapsule):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.inp = self.add_input("in")
        self.out = self.add_output("out")
        self.out.set_activate_handler(self._activate)

    async def _activate(self, activate):
        if activate:
            await self.start()
        else:
            await self.stop()

    async def _handle_input(self, name, data):
        out = await self.transform(data)
        if out is not None:
            await self.out.push(out)

    async def start(self):
        pass

    async def stop(self):
        pass
    
    async def transform(self, data):
        raise NotImplementedError("Override async def transform(self, data)")
