import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from vpipe.core.port import VpPort

class TestPort(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.port = VpPort("test_port")

    async def test_push_calls_chain_callback(self):
        chain_callback = AsyncMock()
        self.port.set_chain_callback(chain_callback)
        await self.port.push("test_data")
        chain_callback.assert_awaited_once_with("test_port", "test_data")

    async def test_push_propagates_to_targets(self):
        target_port = MagicMock(spec=VpPort)
        target_port.push = AsyncMock()
        self.port.link(target_port)
        await self.port.push("test_data")
        target_port.push.assert_awaited_once_with("test_data")

    def test_link_adds_target(self):
        target_port = MagicMock(spec=VpPort)
        self.port.link(target_port)
        self.assertIn(target_port, self.port._targets)

    def test_emit_signal_on_link(self):
        signal_handler = MagicMock()
        self.port.connect_signal("target_linked", signal_handler)
        target_port = MagicMock(spec=VpPort)
        self.port.link(target_port)
        signal_handler.assert_called_once_with(target=target_port)

    async def test_emit_signal_on_push(self):
        signal_handler = MagicMock()
        self.port.connect_signal("data_pushed", signal_handler)
        await self.port.push("test_data")
        signal_handler.assert_called_once_with(data="test_data")

    async def test_start_task_runs_function(self):
        async def sample_task(port):
            port.sample_data = "task_running"
            await asyncio.sleep(0.05)

        self.port.start_task(sample_task, self.port)
        await asyncio.sleep(0.1)
        self.assertEqual(self.port.sample_data, "task_running")
        self.port.stop_task()
        self.assertIsNone(self.port._task)

    async def test_stop_task_cancels_running_task(self):
        async def sample_task(port):
            while True:
                await asyncio.sleep(0.1)
        self.port.start_task(sample_task, self.port)
        await asyncio.sleep(0.1)
        self.port.stop_task()
        self.assertIsNone(self.port._task)

if __name__ == "__main__":
    unittest.main()
