import unittest
import asyncio
from unittest.mock import AsyncMock, patch
from vpipe.core.audiosrc import VpAudioSource
from vpipe.core.config import GLOBAL_AUDIO_CONFIG

class DummyAudioSource(VpAudioSource):
    def __init__(self):
        super().__init__("dummy", GLOBAL_AUDIO_CONFIG)
        self.opened = False
        self.closed = False
        self.read_chunk_called = False
        self.read_chunk_args = None
        self.chunk_to_return = "chunk"
    async def open(self):
        self.opened = True
    async def close(self):
        self.closed = True
    async def read_chunk(self, length):
        self.read_chunk_called = True
        self.read_chunk_args = length
        return self.chunk_to_return

class TestVpAudioSource(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.src = DummyAudioSource()

    async def test_start_and_stop(self):
        await self.src.start()
        self.assertTrue(self.src.opened)
        self.assertIsNotNone(self.src.next_time)
        await self.src.stop()
        self.assertTrue(self.src.closed)
        self.assertIsNone(self.src.next_time)

    async def test_read_calls_read_chunk_and_timing(self):
        self.src.next_time = asyncio.get_running_loop().time() - 1
        result = await self.src.read()
        self.assertTrue(self.src.read_chunk_called)
        self.assertEqual(self.src.read_chunk_args, self.src.audio_config.blocksize)
        self.assertEqual(result, self.src.chunk_to_return)

    async def test_read_waits_if_needed(self):
        self.src.next_time = asyncio.get_running_loop().time() + 0.05
        with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
            await self.src.read()
            sleep_mock.assert_awaited()

    async def test_read_timing_control_cycle(self):
        self.src.next_time = asyncio.get_running_loop().time()
        with patch("asyncio.sleep", new=AsyncMock()) as sleep_mock:
            await self.src.read()  # First call, should not sleep
            sleep_mock.assert_not_awaited()
            # Second call: next_time has been increased by cycle_s, so should sleep for the cycle
            await self.src.read()
            sleep_mock.assert_awaited()
            # Check that the sleep time is approximately equal to cycle_s
            sleep_args = sleep_mock.await_args[0][0]
            self.assertAlmostEqual(sleep_args, self.src.cycle_s, delta=0.01)

    async def test_not_implemented_methods(self):
        base = VpAudioSource()
        with self.assertRaises(NotImplementedError):
            await base.open()
        with self.assertRaises(NotImplementedError):
            await base.close()
        with self.assertRaises(NotImplementedError):
            await base.read_chunk(10)

if __name__ == "__main__":
    unittest.main()
