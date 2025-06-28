import asyncio
import threading
from concurrent.futures import CancelledError

class AsyncLoopThread:
    """
    AsyncLoopThread
    ----------------
    Manages a dedicated thread running its own asyncio event loop.
    Allows submitting coroutines safely from other threads.

    API:
        - start(): Start the thread and event loop.
        - await run(coro): Submit a coroutine to run in the loop.
        - await stop(): Stop the event loop and join the thread.
    """
    def __init__(self):
        # Dedicated thread for the event loop
        self._thread = threading.Thread(target=self._thread_main, daemon=True)
        # Synchronization event to signal loop readiness
        self._loop_ready = threading.Event()
        self._loop = None
        self._stopping = False

    def start(self):
        """
        Start the thread and initialize the event loop.
        """
        self._thread.start()
        self._loop_ready.wait()

    def _thread_main(self):
        """
        Entry point for the thread: create and run the event loop.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop_ready.set()
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def _submit_coroutine(self, coro):
        """
        Submit a coroutine to be executed in the event loop.
        Returns a concurrent.futures.Future.
        """
        if self._stopping:
            raise RuntimeError("AsyncLoopThread is stopping.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future

    async def run(self, coro):
        """
        Submit a coroutine and await its result.
        Example:
            result = await loop_thread.run(some_async_function())
        """
        fut = self._submit_coroutine(coro)
        return await asyncio.wrap_future(fut)

    async def stop(self):
        """
        Stop the event loop and wait for the thread to exit.
        """
        if not self._stopping:
            self._stopping = True
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()
