import asyncio
import unittest
from unittest.mock import AsyncMock
from vpipe.core.queue import VpQueue, DrainPolicy
from vpipe.core.capsule import VpCapsule, VpState


class TestQueue(unittest.IsolatedAsyncioTestCase):
    class Sink(VpCapsule):
        def __init__(self, output_data, name=None):
            super().__init__(name)
            self.add_input("in")
            self.output_data = output_data

        async def process(self, data):
            self.output_data.append(data)
        
        async def _handle_input(self, name, data):
            await self.process(data)

    async def run_pipeline(self, queue, sink, inputs):
        for data in inputs:
            await queue.get_input("in").push(data)

        asyncio.create_task(queue.run())
        asyncio.create_task(sink.run())
        await asyncio.sleep(0.1)

    async def test_queue_basic(self):
        queue = VpQueue(name="test_queue", maxsize=2, leaky=DrainPolicy.NONE)
        await queue.set_state(VpState.RUNNING)
        output_data = []
        sink = self.Sink(output_data, name="sink")

        queue >> sink
        await self.run_pipeline(queue, sink, ["data1", "data2"])

        self.assertEqual(output_data, ["data1", "data2"])

    async def test_queue_downstream_policy(self):
        queue = VpQueue(name="test_queue", maxsize=2, leaky=DrainPolicy.DOWNSTREAM)
        await queue.set_state(VpState.RUNNING)
        output_data = []
        sink = self.Sink(output_data, name="sink")

        queue >> sink
        await self.run_pipeline(queue, sink, ["data1", "data2", "data3"])

        self.assertEqual(output_data, ["data2", "data3"])

    async def test_queue_upstream_policy(self):
        queue = VpQueue(name="test_queue", maxsize=2, leaky=DrainPolicy.UPSTREAM)
        await queue.set_state(VpState.RUNNING)
        output_data = []
        sink = self.Sink(output_data, name="sink")

        queue >> sink
        await self.run_pipeline(queue, sink, ["data1", "data2", "data3"])

        self.assertEqual(output_data, ["data1", "data2"])

    async def test_handle_input(self):
        class DummyCapsule(VpCapsule):
            async def _handle_input(self, name, data):
                await self.process(data)

        capsule = DummyCapsule(name="test_capsule")
        capsule.process = AsyncMock()

        await capsule._handle_input("in", "data")
        capsule.process.assert_awaited_once_with("data")


if __name__ == "__main__":
    unittest.main()
