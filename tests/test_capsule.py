import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from vpipe.core.capsule import VpCapsule

class TestCapsule(unittest.IsolatedAsyncioTestCase):
    def test_input_and_output_registration(self):
        capsule = VpCapsule("test")
        port_in = capsule.add_input("in")
        port_out = capsule.add_output("out")
        self.assertIn("in", capsule._input_ports)
        self.assertIn("out", capsule._output_ports)
        self.assertIs(capsule.get_input("in"), port_in)
        self.assertIs(capsule.get_output("out"), port_out)

    async def test_handle_input_calls_process(self):
        class DummyCapsule(VpCapsule):
            async def _handle_input(self, name, data):
                await self.process(data)
        capsule = DummyCapsule("test")
        capsule.process = AsyncMock()
        await capsule._handle_input("in", "data")
        capsule.process.assert_awaited_once_with("data")

    def test_rshift_links_ports(self):
        capsule1 = VpCapsule("e1")
        capsule2 = VpCapsule("e2")
        port_out = capsule1.add_output("out")
        port_in = capsule2.add_input("in")
        port_out.link = MagicMock()
        capsule1 >> capsule2
        port_out.link.assert_called_once_with(port_in)

    def test_get_input_raises_keyerror(self):
        capsule = VpCapsule()
        with self.assertRaises(KeyError):
            capsule.get_input("nonexistent")

    def test_get_output_raises_keyerror(self):
        capsule = VpCapsule()
        with self.assertRaises(KeyError):
            capsule.get_output("nonexistent")

    def test_default_name(self):
        capsule = VpCapsule()
        self.assertEqual(capsule.name, "VpCapsule")

    async def test_run_does_nothing(self):
        capsule = VpCapsule()
        await capsule.run()

    async def test_state_property_and_setter(self):
        capsule = VpCapsule()
        states = []
        capsule.connect_signal("state_changed", lambda old_state, new_state: states.append((old_state, new_state)))
        capsule.state = capsule.state  # No change
        self.assertEqual(states, [(capsule.state, capsule.state)])
        capsule.state = type(capsule.state).READY
        self.assertEqual(capsule.state, type(capsule.state).READY)

    async def test_bus_and_post_message(self):
        from vpipe.core.bus import VpBus
        capsule = VpCapsule()
        bus = VpBus()
        capsule.bus = bus
        msg = object()
        capsule.post_message(msg)
        await asyncio.sleep(0.05)  # Let the task run
        # Can't check bus.messages, but can check no error
        self.assertIs(capsule.bus, bus)

    async def test_set_state_and_change_state(self):
        capsule = VpCapsule()
        # Test direct transition
        result = await capsule.set_state(type(capsule.state).READY)
        self.assertTrue(result)
        self.assertEqual(capsule.state, type(capsule.state).READY)
        # Test multi-step transition and record calls
        capsule.state = type(capsule.state).RUNNING
        calls = []
        orig_change_state = capsule.change_state
        async def record_change_state(transition):
            calls.append(transition)
            return await orig_change_state(transition)
        capsule.change_state = record_change_state
        result = await capsule.set_state(type(capsule.state).NULL)
        self.assertTrue(result)
        self.assertEqual(capsule.state, type(capsule.state).NULL)
        # Check that all intermediate transitions were called
        from vpipe.core.capsule import VpStateTransition, VpState
        expected = [
            VpStateTransition.RUNNING_TO_PAUSED,
            VpStateTransition.PAUSED_TO_READY,
            VpStateTransition.READY_TO_NULL
        ]
        self.assertEqual(calls, expected)

    async def test_activate_ports(self):
        capsule = VpCapsule()
        in_port = capsule.add_input("in")
        out_port = capsule.add_output("out")
        in_port.activate = AsyncMock()
        out_port.activate = AsyncMock()
        await capsule._activate_ports(True)
        in_port.activate.assert_awaited_with(True)
        out_port.activate.assert_awaited_with(True)

if __name__ == "__main__":
    unittest.main()
