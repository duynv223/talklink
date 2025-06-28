import asyncio
from .basesrc import VpBaseSource
from vpipe.core.config import GLOBAL_AUDIO_CONFIG, AudioConfig


def timing_control(cycle_s_attr="cycle_s", next_time_attr="next_time"):
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            now = asyncio.get_running_loop().time()
            wait_time = getattr(self, next_time_attr) - now

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            setattr(self, next_time_attr,
                    getattr(self, next_time_attr) + getattr(self, cycle_s_attr))

            return await func(self, *args, **kwargs)
        return wrapper
    return decorator


class VpAudioSource(VpBaseSource):
    def __init__(self, name=None, audio_config: AudioConfig = None):
        super().__init__(name)
        self.audio_config = audio_config or GLOBAL_AUDIO_CONFIG

        self.cycle_s = self.audio_config.block_duration
        self.next_time = None

    async def start(self):
        await self.open()
        self.next_time = asyncio.get_running_loop().time()

    async def stop(self):
        await self.close()
        self.next_time = None

    @timing_control(cycle_s_attr="cycle_s", next_time_attr="next_time")
    async def read(self):
        return await self.read_chunk(self.audio_config.blocksize)

    async def open(self):
        raise NotImplementedError("Subclasses must implement open().")

    async def close(self):
        raise NotImplementedError("Subclasses must implement close().")

    async def read_chunk(self, length):
        raise NotImplementedError("Subclasses must implement read_chunk().")
