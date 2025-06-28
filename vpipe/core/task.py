import asyncio
from enum import Enum
from .vpobject import VpObject

class TaskState(Enum):
    STOPPED = 0
    STARTED = 1
    PAUSED = 2

class VpTask(VpObject):
    def __init__(self, func, *args, **kwargs):
        super().__init__("task")
        self.func = func
        self.task = None
        self.args = args
        self.kwargs = kwargs
        self.state = TaskState.STOPPED

    async def _loop(self):
        try:
            while self.state != TaskState.STOPPED:
                if self.state == TaskState.STARTED:
                    await self.func(*self.args, **self.kwargs)
                elif self.state == TaskState.PAUSED:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    def _set_state(self, new_state):
        if not isinstance(new_state, TaskState):
            raise ValueError("Invalid state. Must be a TaskState enum.")
        old_state = self.state
        if old_state == new_state:
            return
        self.state = new_state
        self.emit_signal("state_changed", old_state=old_state, new_state=new_state)

        if new_state == TaskState.STARTED:
            if self.task and not self.task.done():
                self.task.cancel()
            self.task = asyncio.create_task(self._loop())
        elif new_state == TaskState.STOPPED:
            if self.task and not self.task.done():
                self.task.cancel()
                self.task = None

    def start(self):
        self._set_state(TaskState.STARTED)

    def stop(self):
        self._set_state(TaskState.STOPPED)

    def pause(self):
        self._set_state(TaskState.PAUSED)

    def resume(self):
        self._set_state(TaskState.STARTED)

    def get_state(self):
        return self.state
