import unittest
import asyncio
from enum import Enum
from vpipe.core.task import VpTask, TaskState

class TestTask(unittest.IsolatedAsyncioTestCase):
    async def sample_task(self, result, value):
        result.append(value)
        await asyncio.sleep(0.1)

    async def test_task_start(self):
        result = []
        task = VpTask(self.sample_task, result, "test")
        task.start()
        await asyncio.sleep(0.3)
        task.stop()
        self.assertIn("test", result)
        self.assertEqual(task.get_state(), TaskState.STOPPED)

    async def test_task_pause_and_resume(self):
        result = []
        task = VpTask(self.sample_task, result, "test")
        task.start()
        await asyncio.sleep(0.2)
        task.pause()
        state_after_pause = task.get_state()
        await asyncio.sleep(0.2)
        task.resume()
        await asyncio.sleep(0.2)
        task.stop()
        self.assertEqual(state_after_pause, TaskState.PAUSED)
        self.assertIn("test", result)
        self.assertEqual(task.get_state(), TaskState.STOPPED)

    async def test_task_stop(self):
        result = []
        task = VpTask(self.sample_task, result, "test")
        task.start()
        await asyncio.sleep(0.2)
        task.stop()
        state_after_stop = task.get_state()
        await asyncio.sleep(0.2)
        self.assertEqual(state_after_stop, TaskState.STOPPED)
        self.assertIn("test", result)

    async def test_state_changed_signal(self):
        result = []

        def on_state_changed(old_state, new_state):
            result.append((old_state, new_state))

        task = VpTask(self.sample_task, [], None)
        task.connect_signal("state_changed", on_state_changed)
        task.start()
        await asyncio.sleep(0.1)
        task.pause()
        await asyncio.sleep(0.1)
        task.resume()
        await asyncio.sleep(0.1)
        task.stop()

        self.assertIn((TaskState.STOPPED, TaskState.STARTED), result)
        self.assertIn((TaskState.STARTED, TaskState.PAUSED), result)
        self.assertIn((TaskState.PAUSED, TaskState.STARTED), result)
        self.assertIn((TaskState.STARTED, TaskState.STOPPED), result)
