import asyncio
import sounddevice as sd
from .capsule import VpCapsule
from .config import GLOBAL_AUDIO_CONFIG


class VpAudioSink(VpCapsule):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name=name)
        self.audio_config = audio_config or GLOBAL_AUDIO_CONFIG
        
        self.inp = self.add_input("in")
        self.inp.set_activate_handler(self._src_active)
        self._src_lock = asyncio.Lock()
    
    async def _src_active(self, active):
        if active:
            await self.open()
        else:
            async def safe_close():
                async with self._src_lock:
                    await self.close()
            asyncio.create_task(safe_close())
    
    async def _handle_input(self, _, buf):
        async with self._src_lock:
            await self.write(buf)

    async def open(self):
        pass

    async def close(self):
        pass

    async def write(self, buf):
        pass
