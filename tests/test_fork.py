import unittest
import asyncio
from unittest.mock import AsyncMock
from vpipe.core.fork import VpFork

class TestVpFork(unittest.IsolatedAsyncioTestCase):
    async def test_fork_broadcasts_to_all_outputs(self):
        fork = VpFork()
        out1 = fork.fork("out1")
        out2 = fork.fork("out2")
        out1.push = AsyncMock()
        out2.push = AsyncMock()
        await fork._on_data(None, "testdata")
        out1.push.assert_awaited_once_with("testdata")
        out2.push.assert_awaited_once_with("testdata")

    async def test_fork_dynamic_output_names(self):
        fork = VpFork()
        out_a = fork.fork()
        out_b = fork.fork()
        self.assertEqual(out_a.name, "out0")
        self.assertEqual(out_b.name, "out1")

if __name__ == "__main__":
    unittest.main()
