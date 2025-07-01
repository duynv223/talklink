import asyncio
from enum import Enum, auto

from .capsule import VpCapsule


class DrainPolicy(Enum):
    NONE = auto()
    DOWNSTREAM = auto()
    UPSTREAM = auto()


class VpQueue(VpCapsule):
    def __init__(self, name=None, maxsize=0, leaky: DrainPolicy = DrainPolicy.NONE):
        super().__init__(name or "queue")
        self._queue = asyncio.Queue(maxsize=maxsize)
        self._maxsize = maxsize
        self._leaky = leaky

        self.add_input("in").set_activate_handler(self._queue_src_active)
        self.add_output("out")

    async def _queue_src_active(self, active):
        if active:
            await self.flush()
            self.get_input("in").start_task(self._process_queue, self.get_output("out"))
        else:
            self.get_input("in").stop_task()

    async def _process_queue(self, port):
        data = await self._queue.get()
        await port.push(data)
        self._queue.task_done()

    async def _handle_input(self, name, data):
        if self._maxsize > 0 and self._queue.full():
            # self.logger.warning(f'{self.name} drop data due to full queue')
            if self._leaky == DrainPolicy.DOWNSTREAM:
                try:
                    await self._queue.get()
                    self._queue.task_done()
                except asyncio.QueueEmpty:
                    pass
            elif self._leaky == DrainPolicy.UPSTREAM:
                return
        await self._queue.put(data)

    async def process(self, data):
        pass

    async def flush(self):
        # self.logger.warning(f'{self.name} flush')
        items = []
        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                self._queue.task_done()
                items.append(item)
            except asyncio.QueueEmpty:
                break
        return len(items)