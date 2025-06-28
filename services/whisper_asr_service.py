from vpipe.capsules.services.asr import ASRServiceInterface
from typing import Any, Optional, Tuple
import numpy as np
import threading
import websocket
import json
import struct
import queue

LANG_MODEL_MAP = {
    "en": {"model": "large-v3", "language": "en"},
    "ja": {"model": "large-v3", "language": "ja"},
    "vi": {"model": "large-v3", "language": "vi"},
}

SERVER_URL = "ws://localhost:8012"

class WhisperASRService(ASRServiceInterface):
    def __init__(self, lang: str = "en"):
        if lang not in LANG_MODEL_MAP:
            raise ValueError(f"Unsupported language: {lang}")
        self.server_url = SERVER_URL
        self.language = LANG_MODEL_MAP[lang]["language"]

        self.ws = None
        self.ws_thread = None
        self.recv_queue = queue.Queue()
        self._connected = threading.Event()
        self._stop_flag = threading.Event()
        
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
            raise RuntimeError("Timeout waiting for server readiness")
        
    async def stop(self):
        print("Trigger STOP by system control")
        self._connected.clear()
        self._stop_flag.set()
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()

    async def transcribe(self, buf: np.ndarray) -> Optional[Tuple[str, bool]]:
        if not self.ws or not self.ws.sock or not self.ws.sock.connected:
            raise RuntimeError("WebSocket is not connected")

        header = json.dumps({
            "language": self.language,
        }).encode('utf-8')
        header_len = struct.pack("<I", len(header))
        pcm16 = buf[:, 0].astype(np.int16).tobytes()
        message = header_len + header + pcm16

        try:
            self.ws.send(message, opcode=websocket.ABNF.OPCODE_BINARY)
        except Exception:
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
                message = message.decode("utf-8", errors="ignore")

            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "status" and data.get("ready"):
                self._connected.set()

            elif msg_type == "diarizedTranscript":
                for seg in data.get("segments", []):
                    speaker = seg.get("speaker", "unknown")
                    text = seg.get("text", "").strip()
                    if text:
                        message_str = f"[{speaker}]: {text}"
                        self.recv_queue.put((message_str, True))
        except Exception:
            pass

