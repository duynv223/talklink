import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional
import time
from vpipe.core.vpobject import VpObject

@dataclass
class VpBusMessage:
    msg_type: str
    payload: Any
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def __repr__(self):
        return (f"<VpBusMessage event_type={self.msg_type}, "
                f"payload={self.payload!r}, source={self.source!r}, "
                f"timestamp={self.timestamp:.3f}>")


class VpBus(VpObject):
    def __init__(self, name=None):
        super().__init__(name)
        self._queue = asyncio.Queue()
        self._watchers = []

    async def post(self, message: VpBusMessage):
        self.emit_signal("message", message=message)
        await self._queue.put(message)

        for watcher in self._watchers:
            await watcher(message)

    def add_watch(self, callback):
        self._watchers.append(callback)

    def remove_watch(self, callback):
        if callback in self._watchers:
            self._watchers.remove(callback)

    async def poll(self, timeout=None):
        try:
            if timeout is None:
                return await self._queue.get()
            else:
                return await asyncio.wait_for(self._queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
