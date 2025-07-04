from vpipe.capsules.services.asr import ASRServiceInterface
from typing import Any, Optional, Tuple
import numpy as np
import json
import struct
import asyncio
import websockets
import logging

LANG_MODEL_MAP = {
    "en": {"model": "large-v3", "language": "en"},
    "ja": {"model": "large-v3", "language": "ja"},
    "vi": {"model": "large-v3", "language": "vi"},
}

SERVER_URL = "ws://localhost:8012"
logger = logging.getLogger(__name__)


class WhisperASRService(ASRServiceInterface):
    def __init__(self, lang='en', settings={}):
        if lang not in LANG_MODEL_MAP:
            raise ValueError(f"Unsupported language: {lang}")
        self.server_url = settings.get("url", SERVER_URL)
        self.language = LANG_MODEL_MAP[lang]["language"]

        self._ws = None
        self._buffer = bytearray()
        self._recv_task = None
        self._send_task = None
        self._recv_queue = asyncio.Queue()
        self._connected_event = asyncio.Event()
        self.min_send_size = 1024

        self._starting = False
        self._started = False
        self._stopped = True

    async def switch_lang(self, lang):
        """ Support dynamic language switching """
        self.language = LANG_MODEL_MAP.get(lang, LANG_MODEL_MAP["en"])["language"]

    async def start(self):
        if self._starting or self._started:
            return

        self._starting = True
        self._stopped = False

        try:
            self._buffer.clear()
            self._recv_queue = asyncio.Queue()
            self._connected_event.clear()

            self._ws = await websockets.connect(self.server_url, ping_timeout=None)
            self._recv_task = asyncio.create_task(self._recv_loop())
            self._send_task = asyncio.create_task(self._send_loop())

            await asyncio.wait_for(self._connected_event.wait(), timeout=20)
            self._started = True

        except asyncio.TimeoutError:
            raise RuntimeError("Timeout: failed to connect to ASR server within the expected time.")
        except (websockets.WebSocketException, OSError) as e:
            raise RuntimeError(f"Connection to ASR server failed: {e}")
        finally:
            self._starting = False

    async def stop(self):
        self._stopped = True
        tasks = []

        if self._recv_task:
            self._recv_task.cancel()
            tasks.append(self._recv_task)
            self._recv_task = None

        if self._send_task:
            self._send_task.cancel()
            tasks.append(self._send_task)
            self._send_task = None

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        if self._ws:
            await self._ws.close()
            self._ws = None

        self._buffer.clear()
        self._started = False

    async def transcribe(self, buf: np.ndarray) -> Optional[Tuple[str, bool]]:
        if self._stopped or not self._connected_event.is_set():
            return None

        audio_bytes = buf.astype(np.int16).tobytes()
        self._buffer.extend(audio_bytes)

        try:
            text, speaker, wav_bytes = self._recv_queue.get_nowait()
            return text, True
        except asyncio.QueueEmpty:
            return None

    async def _send_loop(self):
        try:
            while True:
                if len(self._buffer) < self.min_send_size:
                    await asyncio.sleep(0.01)
                    continue

                chunk = self._buffer[:self.min_send_size]
                self._buffer = self._buffer[self.min_send_size:]

                header = json.dumps({"language": self.language}).encode("utf-8")
                header_len = struct.pack("<I", len(header))
                message = header_len + header + chunk

                await self._ws.send(message)

        except asyncio.CancelledError:
            pass
        except (websockets.WebSocketException, OSError) as e:
            self.stop()
            raise RuntimeError(f"Connection to ASR server failed during send loop: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in send loop: {e}")

    async def _recv_loop(self):
        try:
            async for msg in self._ws:
                if isinstance(msg, bytes) and len(msg) >= 4:
                    header_len = struct.unpack("<I", msg[:4])[0]
                    header_json = msg[4:4 + header_len].decode("utf-8", errors="ignore")
                    header = json.loads(header_json)
                    text = header.get("text", "").strip()
                    speaker = header.get("speaker", "unknown")
                    wav_bytes = msg[4 + header_len:]
                    
                    if text:
                        result = {
                            "text": text,
                            "speaker": speaker,
                            "origin_audio": wav_bytes,
                            "is_final": True
                        }
                        await self._recv_queue.put(result)

                elif isinstance(msg, str):
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "status" and data.get("ready"):
                            self._connected_event.set()
                    except Exception as e:
                        logger.error(f"[{self.language}] Failed to parse JSON message: {e}")

        except asyncio.CancelledError:
            pass
        except (websockets.WebSocketException, OSError) as e:
            self.stop()
            raise RuntimeError(f"Connection to ASR server failed during receive loop: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in receive loop: {e}")