import asyncio
from vpipe.core.capsule import VpCapsule, VpState, VpStateTransition

class VpBaseSource(VpCapsule):
    def __init__(self, name=None):
        super().__init__(name)
        self.out = self.add_output("out")
        self.out.set_activate_handler(self._src_active)
        self._src_lock = asyncio.Lock()

    def play(self):
        self.out.start_task(self._src_loop)
    
    async def _src_active(self, active):
        if active:
            await self.start()
            self.out.start_task(self._src_loop)
        else:
            async def safe_close():
                async with self._src_lock:
                    await self.stop()
            asyncio.create_task(safe_close())

    async def _src_loop(self):
        if self.state in (VpState.PAUSED, VpState.RUNNING):        
            async with self._src_lock:
                data = await self.read()

            if self.state == VpState.RUNNING and data is not None:
                await self.out.push(data)
        await asyncio.sleep(0)

    async def start(self):
        raise NotImplementedError("Subclasses must implement open.")

    async def stop(self):
        raise NotImplementedError("Subclasses must implement close.")
    
    async def read(self):
        raise NotImplementedError("Subclasses must implement read.")
