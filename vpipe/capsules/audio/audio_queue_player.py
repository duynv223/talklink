import asyncio
import numpy as np
from vpipe.core.audiosrc import VpAudioSource
from pydub import AudioSegment
from vpipe.core.config import GLOBAL_AUDIO_CONFIG


class VpAudioQueuePlayer(VpAudioSource):
    def __init__(self, name, speed=1.0, audio_config=None):
        super().__init__(name=name, audio_config=audio_config or GLOBAL_AUDIO_CONFIG)

        self.speed = speed
        self.inp = self.add_input("in")
        self.audio_queue = asyncio.Queue(maxsize=10)
        self.samples = None
        self.position = 0
        self.silence = np.zeros((self.audio_config.blocksize,
                                 self.audio_config.format.channels), 
                                 dtype=self.audio_config.format.dtype)
    
    async def set_prop(self, prop, value):
        match prop:
            case "speed":
                self.speed = value
            case _:
                raise ValueError(f"Unknown property: {prop}")

    def stretch_audio(self, audio, speed, fmt):
        seg = AudioSegment(
            audio,
            frame_rate=fmt.rate,
            sample_width=fmt.sample_size,
            channels=fmt.channels
        )

        if speed != 1.0:
            seg = seg._spawn(seg.raw_data, overrides={
                "frame_rate": int(seg.frame_rate * speed)
            }).set_frame_rate(fmt.rate)

        return seg.raw_data

    async def _handle_input(self, name, buf):
        fmt = self.audio_config.format
        try:
            stretched_buf = self.stretch_audio(buf.tobytes(), self.speed, fmt)
            stretched_buf = np.frombuffer(stretched_buf, dtype=fmt.dtype).reshape((-1, fmt.channels))
            await asyncio.wait_for(self.audio_queue.put(stretched_buf), timeout=1.0)

        except asyncio.TimeoutError:
            print("Warning: Audio queue full, dropping buffer")

    async def open(self):
        pass

    async def close(self):
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except:
                pass
        self.samples = None
        self.position = 0

    async def read_chunk(self, length):
        if self.samples is None or self.position >= len(self.samples):
            try:
                self.samples = await asyncio.wait_for(self.audio_queue.get(), timeout=0.01)
                self.position = 0
                self.audio_queue.task_done()
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                return self.silence

        end = min(self.position + length, len(self.samples))
        block = self.samples[self.position:end]
        self.position = end

        if len(block) < length:
            block = np.pad(block, ((0, length - len(block)), (0, 0)), mode='constant', constant_values=0)
            
        return block
