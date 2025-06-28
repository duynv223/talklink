import asyncio
import numpy as np
from vpipe.core.capsule import VpCapsule
from vpipe.core.config import GLOBAL_AUDIO_CONFIG, AudioConfig

class VpAudiopMixer(VpCapsule):
    def __init__(self, name=None, audio_config=None):
        super().__init__(name or "mixer")
        self._audio_config = audio_config or GLOBAL_AUDIO_CONFIG
        self._buffers = {}
        self._cond = asyncio.Condition()

        self.add_output("out").set_activate_handler(self._src_active)

    def add_input(self, name):
        port = super().add_input(name)
        self._buffers[name] = None

        port.set_property("volume", 1.0)
        port.set_property("mute", False)

        return port

    async def _handle_input(self, name, chunk):
        if not isinstance(chunk, np.ndarray):
            raise ValueError(f"Invalid chunk on '{name}'")

        async with self._cond:
            while self._buffers[name] is not None:
                await self._cond.wait()

            self._buffers[name] = chunk
            self._cond.notify_all()  # wake mixer

    def _src_active(self, active):
        port = self.get_output("out")
        if active:
            port.start_task(self._mixer_task, port)
        else:
            port.stop_task()

    async def _mixer_task(self, out_port):
        while True:
            async with self._cond:
                await self._cond.wait_for(lambda: all(v is not None for v in self._buffers.values()))

                chunks = []
                dtype = None

                for name, buf in self._buffers.items():
                    port = self.get_input(name)
                    volume = port.get_property("volume")
                    if volume is None:
                        volume = 1.0
                    mute = port.get_property("mute")
                    if mute is None:
                        mute = False

                    data = np.zeros_like(buf, dtype=np.float32) if mute else buf.astype(np.float32) * volume
                    chunks.append(data)
                    if dtype is None:
                        dtype = buf.dtype

                mix = np.mean(chunks, axis=0).round().astype(dtype)
                self._buffers = {k: None for k in self._buffers}
                self._cond.notify_all()

            await out_port.push(mix)
            await asyncio.sleep(0)
