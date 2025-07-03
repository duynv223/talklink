from vpipe.capsules.services.asr import ASRServiceInterface
from typing import Any, Optional, Tuple
import numpy as np
import threading
import websocket
import json
import struct
import queue
import logging

LANG_MODEL_MAP = {
    "en": {"model": "large-v3", "language": "en"},
    "ja": {"model": "large-v3", "language": "ja"},
    "vi": {"model": "large-v3", "language": "vi"},
}

SERVER_URL = "ws://localhost:8012"

logger = logging.getLogger(__name__)


class WhisperASRService(ASRServiceInterface):
    def __init__(self, *args: Any, **kwargs: Any):
        logger.info(f"Initializing Whisper ASR service with args: {args}, kwargs: {kwargs}")
        lang = kwargs.get("lang", "en")
        url = kwargs.get("url", SERVER_URL)

        if lang not in LANG_MODEL_MAP:
            raise ValueError(f"Unsupported language: {lang}")
        self.server_url = url
        self.language = LANG_MODEL_MAP[lang]["language"]

        self.ws = None
        self.ws_thread = None
        self.recv_queue = queue.Queue()
        self._connected = threading.Event()
        self._stop_flag = threading.Event()
        self._buffer = bytearray()
        self.min_send_size = 3200 # 0.1s (do not change this value)
        
    async def start(self):
        self.ws = websocket.WebSocketApp(
            self.server_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.ws_thread.start()

        if not self._connected.wait(timeout=20):
            raise RuntimeError("Timeout waiting for Whisper ASR server readiness")
        
    async def stop(self):
        self._connected.clear()
        self._stop_flag.set()
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()

    async def transcribe(self, audio: bytes) -> Optional[Tuple[str, bool]]:
        if not self.ws or not self.ws.sock or not self.ws.sock.connected:
            raise RuntimeError("WebSocket is not connected")

        self._buffer.extend(audio)

        if len(self._buffer) < self.min_send_size:
            return None

        # Construct message
        header = json.dumps({
            "language": self.language,
        }).encode('utf-8')
        header_len = struct.pack("<I", len(header))
        message = header_len + header + self._buffer[:self.min_send_size]
        self._buffer = self._buffer[self.min_send_size:]

        try:
            self.ws.send(message, opcode=websocket.ABNF.OPCODE_BINARY)
        except Exception as e:
            return None

        try:
            return self.recv_queue.get_nowait()
        except queue.Empty:
            return None

    def _on_open(self, ws):
        # Connection established, wait for 'status' message
        pass

    def _on_close(self, ws, code, msg):
        self._connected.clear()
        self._last_error = RuntimeError(f"WebSocket closed (code={code}, msg={msg})")
        self._stop_flag.set()

    def _on_error(self, ws, error):
        self._connected.clear()
        self._last_error = RuntimeError(f"WebSocket error: {error}")
        self._stop_flag.set()

    def _on_message(self, ws, message):
        try:
            if isinstance(message, bytes):
                if len(message) < 4:
                    print("[WARN] Received short binary message.")
                    return

                header_len = struct.unpack("<I", message[:4])[0]
                header_json = message[4:4 + header_len].decode("utf-8", errors="ignore")
                header = json.loads(header_json)
                text = header.get("text", "").strip()
                speaker = header.get("speaker", "unknown")
                wav_bytes = message[4 + header_len:] # samplerate=16000, format="WAV"

                if text:
                    result = f"[{speaker}]: {text}"
                    self.recv_queue.put((result, True))

            else:
                data = json.loads(message)
                if data.get("type") == "status" and data.get("ready"):
                    print("WhisperASRService server is ready.")
                    self._connected.set()

        except Exception as e:
            print(f"[ERROR] Failed to process message: {e}")

