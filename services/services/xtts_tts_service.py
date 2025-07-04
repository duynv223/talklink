import asyncio
import io
import json
import numpy as np
import websockets
import soundfile as sf
from vpipe.capsules.services.tts import TTSServiceInterface
from pydub import AudioSegment
import logging
import base64

SERVER_URL = "ws://localhost:8765"

logger = logging.getLogger(__name__)


class XttsTTSService(TTSServiceInterface):
    def __init__(self, *args, **kwargs):
        logger.info(f"Initializing Xtts TTS service with args: {args}, kwargs: {kwargs}")
        self.server_url = kwargs.get("url", SERVER_URL)
        self.websocket = None

    async def start(self):
        # Open connection once (optional: keep alive across calls)
        self.websocket = await websockets.connect(self.server_url, ping_timeout=None)
        logger.info("XTTS websocket openned")

    async def stop(self):
        if self.websocket:
            logger.info("XTTS websocket closed")
            await self.websocket.close()

    async def synthesize(self, text: str, lang: str, ref_voice: bytearray = None, speaker_id: str = None) -> bytes:
        if not text or not lang:
            raise ValueError("Both `text` and `lang` must be provided.")

        # Prepare JSON-safe payload
        payload = {
            "text": text,
            "lang": lang,
            "speaker_id": speaker_id,
            "wav_bytes": base64.b64encode(ref_voice).decode("utf-8") if ref_voice else None,
        }

        logger.info(f"[XTTS] Sending payload: lang={lang}, text='{text} ...'")

        await self.websocket.send(json.dumps(payload))

        response = await self.websocket.recv()

        if isinstance(response, bytes):
            # Convert .wav bytes to mono 16kHz int16 numpy
            audio = AudioSegment.from_file(io.BytesIO(response), format="wav")
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            out = np.frombuffer(audio.raw_data, dtype=np.int16)
            return out

        logger.error(f"[XTTS] Invalid response from server: {response}")
        return np.zeros(16000, dtype=np.int16)  # 1 second of silence fallback
