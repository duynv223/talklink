import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from vpipe.core.composite import VpComposite
from vpipe.core.capsule import VpCapsule

class TestCapsule(VpCapsule):
    async def process(self, data):
        self.processed_data = data.upper()
        if self._output_ports:
            await self.get_output("out").push(self.processed_data)

class TestSink(VpCapsule):
    def __init__(self):
        super().__init__(use_task=True)
        self.add_input("in")
        self.received_data = []

    async def process(self, data):
        self.received_data.append(data)

class TestComposite(unittest.IsolatedAsyncioTestCase):
    async def test_composite_processing(self):
        # Create test capsules
        capsule1 = TestCapsule(name="Capsule1")
        capsule1.add_input("in")  # Add input port "in" to capsule1
        capsule1.add_output("out")
        
        capsule2 = TestCapsule(name="Capsule2")
        capsule2.add_input("in")
        capsule2.add_output("out")
        
        capsule3 = TestCapsule(name="Capsule3")
        capsule3.add_input("in")
        capsule3.add_output("out")  # Add output port "out" to capsule3

        # Create composite and add capsules
        composite = VpComposite(name="Composite")
        composite.add(capsule1)
        composite.add(capsule2)
        composite.add(capsule3)

        # Connect capsules inside the composite
        capsule1 >> capsule2 >> capsule3

        # Expose composite ports
        composite.expose_input("in", capsule1.get_input("in"))

        # Add a TestSink to capture output
        sink = TestSink()
        capsule3 >> sink

        # Simulate external input
        await composite.get_input("in").push("test_data")

        # Run the composite and sink
        await asyncio.gather(
            composite.run(),
            sink.run()
        )

        # Verify the output
        self.assertEqual(sink.received_data, ["TEST_DATA"])

    def setUp(self):
        self.composite = VpComposite(name="test_composite")

    def test_add_capsule(self):
        capsule = MagicMock(spec=VpCapsule)
        self.composite.add(capsule)
        self.assertIn(capsule, self.composite._capsules)

    def test_expose_input(self):
        internal_port = MagicMock()
        self.composite.expose_input("input1", internal_port)
        self.assertIn("input1", self.composite._input_ports)
        self.assertEqual(self.composite._input_ports["input1"], internal_port)

    def test_expose_output(self):
        internal_port = MagicMock()
        self.composite.expose_output("output1", internal_port)
        self.assertIn("output1", self.composite._output_ports)
        self.assertEqual(self.composite._output_ports["output1"], internal_port)

    def test_rshift_operator(self):
        other = MagicMock(spec=VpCapsule)
        self.composite.get_output = MagicMock()
        other.get_input = MagicMock()
        self.composite >> other
        self.composite.get_output.assert_called_with("out")
        other.get_input.assert_called_with("in")

    def test_process(self):
        capsule1 = AsyncMock(spec=VpCapsule)
        capsule2 = AsyncMock(spec=VpCapsule)
        self.composite.add(capsule1)
        self.composite.add(capsule2)

        data = {"key": "value"}
        asyncio.run(self.composite.process(data))

        capsule1.process.assert_awaited_with(data)
        capsule2.process.assert_awaited_with(data)

    def test_run(self):
        capsule1 = AsyncMock(spec=VpCapsule)
        capsule2 = AsyncMock(spec=VpCapsule)
        capsule1._use_task = True
        capsule2._use_task = False
        capsule1.run = AsyncMock()
        capsule2.run = AsyncMock()

        self.composite.add(capsule1)
        self.composite.add(capsule2)

        asyncio.run(self.composite.run())

        capsule1.run.assert_awaited()
        capsule2.run.assert_not_awaited()

if __name__ == "__main__":
    unittest.main()
