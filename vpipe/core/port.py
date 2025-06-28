__author__ = "DuyNV4 <duynv4@fpt.com>"

from .vpobject import VpObject
from .task import VpTask
import asyncio


class VpPort(VpObject):
    def __init__(self, name):
        super().__init__(name)
        self._targets = []
        self._chain_callback = None
        self._task = None
        self._activate_handler = None

    def set_chain_callback(self, callback):
        self._chain_callback = callback

    async def push(self, data):
        if self._chain_callback:
            await self._chain_callback(self.name, data)
        for t in self._targets:
            await t.push(data)
        self.emit_signal("data_pushed", data=data)

    def link(self, target):
        if isinstance(target, VpPort):
            self._targets.append(target)
            self.emit_signal("target_linked", target=target)
        elif hasattr(target, "get_input") and "in" in target._input_ports:
            self._targets.append(target.get_input("in"))
            self.emit_signal("target_linked", target=target.get_input("in"))
        else:
            raise ValueError("Target must be a VpPort or an capsule with an input port named 'in'.")
    
    def unlink(self, target):
        if target in self._targets:
            self._targets.remove(target)
            self.emit_signal("target_unlinked", target=target)
        else:
            raise ValueError("Target not linked to this port.")
    
    def __rshift__(self, target):
        self.link(target)
        return target

    def start_task(self, func, *args, **kwargs):
        self._task = VpTask(func, *args, **kwargs)
        self._task.start()

    def stop_task(self):
        if self._task:
            self._task.stop()
            self._task = None

    def set_activate_handler(self, func):
        self._activate_handler = func

    async def activate(self, active=True):
        if self._activate_handler:
            if asyncio.iscoroutinefunction(self._activate_handler):
                await self._activate_handler(active)
            else:
                self._activate_handler(active)
