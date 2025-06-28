import asyncio
import numpy as np
import unittest
from unittest import mock
from vpipe.capsules.audio.audio_mixer import VpAudiopMixer


class TestVAudiopMixer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mixer = VpAudiopMixer()

    async def test_add_audio_input(self):
        port = self.mixer.add_input("input1")
        self.assertIn("input1", self.mixer._buffers)
        self.assertEqual(port.get_property("volume"), 1.0)
        self.assertEqual(port.get_property("mute"), False)

    async def test_on_input(self):
        self.mixer.add_input("input1")
        chunk = np.array([1, 2, 3], dtype=np.int16)
        await self.mixer._handle_input("input1", chunk)
        self.assertTrue(np.array_equal(self.mixer._buffers["input1"], chunk))

    async def _run_mixer_once(self, out_port):
        # Helper to run mixer task until first push
        task = asyncio.create_task(self.mixer._mixer_task(out_port))
        while not out_port.push.await_count:
            await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    async def test_mixer_task(self):
        self.mixer.add_input("input1")
        self.mixer.add_input("input2")

        chunk1 = np.array([1, 2, 3], dtype=np.int16)
        chunk2 = np.array([4, 5, 6], dtype=np.int16)

        await self.mixer._handle_input("input1", chunk1)
        await self.mixer._handle_input("input2", chunk2)

        out_port = self.mixer.get_output("out")
        out_port.push = mock.AsyncMock()

        await self._run_mixer_once(out_port)

        out_port.push.assert_called_once()
        mixed_chunk = out_port.push.call_args[0][0]
        self.assertEqual(mixed_chunk.tolist(), np.array([2, 4, 4], dtype=np.int16).tolist())

    async def test_mixer_task_with_different_volumes(self):
        self.mixer.add_input("input1")
        self.mixer.add_input("input2")

        self.mixer.get_input("input1").set_property("volume", 0.5)
        self.mixer.get_input("input2").set_property("volume", 1.0)

        chunk1 = np.array([10, 20, 30], dtype=np.int16)
        chunk2 = np.array([40, 50, 60], dtype=np.int16)

        await self.mixer._handle_input("input1", chunk1)
        await self.mixer._handle_input("input2", chunk2)

        out_port = self.mixer.get_output("out")
        out_port.push = mock.AsyncMock()

        await self._run_mixer_once(out_port)

        out_port.push.assert_called_once()
        mixed_chunk = out_port.push.call_args[0][0]

        volume1 = self.mixer.get_input("input1").get_property("volume")
        volume2 = self.mixer.get_input("input2").get_property("volume")
        expected_chunk = ((chunk1 * volume1 + chunk2 * volume2) / 2).round().astype(np.int16)

        self.assertEqual(mixed_chunk.tolist(), expected_chunk.tolist())

    async def test_mixer_task_with_mute(self):
        self.mixer.add_input("input1")
        self.mixer.add_input("input2")
        self.mixer.get_input("input1").set_property("volume", 1.0)
        self.mixer.get_input("input2").set_property("volume", 1.0)
        self.mixer.get_input("input1").set_property("mute", True)
        chunk1 = np.array([10, 20, 30], dtype=np.int16)
        chunk2 = np.array([40, 50, 60], dtype=np.int16)
        await self.mixer._handle_input("input1", chunk1)
        await self.mixer._handle_input("input2", chunk2)
        out_port = self.mixer.get_output("out")
        out_port.push = mock.AsyncMock()
        await self._run_mixer_once(out_port)
        out_port.push.assert_called_once()
        mixed_chunk = out_port.push.call_args[0][0]
        expected_chunk = (chunk2 / 2).round().astype(np.int16)
        self.assertEqual(mixed_chunk.tolist(), expected_chunk.tolist())

    async def test_handle_input_invalid_type(self):
        self.mixer.add_input("input1")
        with self.assertRaises(ValueError):
            await self.mixer._handle_input("input1", [1, 2, 3])

    def test_add_input_properties(self):
        port = self.mixer.add_input("inputX")
        self.assertEqual(port.get_property("volume"), 1.0)
        self.assertEqual(port.get_property("mute"), False)
        self.assertIn("inputX", self.mixer._buffers)

    def test_src_active_starts_and_stops_task(self):
        out_port = self.mixer.get_output("out")
        out_port.start_task = mock.Mock()
        out_port.stop_task = mock.Mock()
        self.mixer._src_active(True)
        out_port.start_task.assert_called_once()
        self.mixer._src_active(False)
        out_port.stop_task.assert_called_once()

    async def test_mixer_task_single_input(self):
        self.mixer.add_input("input1")
        chunk1 = np.array([7, 8, 9], dtype=np.int16)
        await self.mixer._handle_input("input1", chunk1)
        out_port = self.mixer.get_output("out")
        out_port.push = mock.AsyncMock()
        await self._run_mixer_once(out_port)
        out_port.push.assert_called_once()
        mixed_chunk = out_port.push.call_args[0][0]
        self.assertEqual(mixed_chunk.tolist(), chunk1.tolist())

    async def test_mixer_task_all_inputs_muted(self):
        self.mixer.add_input("input1")
        self.mixer.add_input("input2")
        self.mixer.get_input("input1").set_property("mute", True)
        self.mixer.get_input("input2").set_property("mute", True)
        chunk1 = np.array([1, 2, 3], dtype=np.int16)
        chunk2 = np.array([4, 5, 6], dtype=np.int16)
        await self.mixer._handle_input("input1", chunk1)
        await self.mixer._handle_input("input2", chunk2)
        out_port = self.mixer.get_output("out")
        out_port.push = mock.AsyncMock()
        await self._run_mixer_once(out_port)
        out_port.push.assert_called_once()
        mixed_chunk = out_port.push.call_args[0][0]
        self.assertTrue(np.all(mixed_chunk == 0))


if __name__ == "__main__":
    unittest.main()
