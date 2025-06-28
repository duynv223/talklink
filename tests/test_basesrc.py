import unittest
import asyncio
from unittest.mock import AsyncMock, patch
from vpipe.core.basesrc import VpBaseSource
from vpipe.core.capsule import VpState

class DummySource(VpBaseSource):
    def __init__(self):
        super().__init__("dummy")
        self.started = False
        self.stopped = False
        self.data_to_read = None
        self.read_called = False

    async def start(self):
        self.started = True
    async def stop(self):
        self.stopped = True
    async def read(self):
        self.read_called = True
        return self.data_to_read

class TestVpBaseSource(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.src = DummySource()

    async def test_play_and_src_active_start(self):
        self.src.start = AsyncMock()
        self.src.out.start_task = unittest.mock.Mock()
        await self.src._src_active(True)
        self.src.start.assert_awaited_once()
        self.src.out.start_task.assert_called_once()

    async def test_src_active_stop(self):
        self.src.stop = AsyncMock()
        await self.src._src_active(False)
        await asyncio.sleep(0.05)  # Let safe_close run
        self.src.stop.assert_awaited_once()

    async def test_src_loop_paused_and_running(self):
        self.src.data_to_read = "abc"
        self.src.state = VpState.PAUSED
        self.src.out.push = AsyncMock()
        await self.src._src_loop()
        self.assertTrue(self.src.read_called)
        self.src.out.push.assert_not_awaited()
        self.src.state = VpState.RUNNING
        self.src.read_called = False
        await self.src._src_loop()
        self.assertTrue(self.src.read_called)
        self.src.out.push.assert_awaited_with("abc")

    async def test_src_loop_not_paused_or_running(self):
        self.src.state = VpState.NULL
        self.src.read_called = False
        await self.src._src_loop()
        self.assertFalse(self.src.read_called)

    async def test_not_implemented_methods(self):
        base = VpBaseSource()
        with self.assertRaises(NotImplementedError):
            await base.start()
        with self.assertRaises(NotImplementedError):
            await base.stop()
        with self.assertRaises(NotImplementedError):
            await base.read()

if __name__ == "__main__":
    unittest.main()
