import asyncio
import io
import json
import numpy as np
import websockets
import soundfile as sf
from vpipe.capsules.services.tts import TTSServiceInterface
from pydub import AudioSegment
import logging

SERVER_URL = "ws://localhost:8765"

logger = logging.getLogger(__name__)


class XttsTTSService(TTSServiceInterface):
    def __init__(self, *args, **kwargs):
        logger.info(f"Initializing Xtts TTS service with args: {args}, kwargs: {kwargs}")
        self.server_url = kwargs.get("url", SERVER_URL)
        self.websocket = None
        self.default_speakers = {
            'vi': "ref/vi_male.wav", 
            'en': 'ref/en.wav', 
            'ja': 'ref/ja.wav'
        }

    async def start(self):
        # Open connection once (optional: keep alive across calls)
        self.websocket = await websockets.connect(self.server_url, ping_timeout=None)
        print("XTTS websocket openned")

    async def stop(self):
        if self.websocket:
            await self.websocket.close()

    async def synthesize(self, text: str, lang: str):
        print("synthesize")

        payload = {
            "lang": lang,
            "text": text,
            "speaker_wav": self.default_speakers[lang]
        }

        print(f"[DEBUG] Sending payload: {payload}")
        await self.websocket.send(json.dumps(payload))
        response = await self.websocket.recv()
        if isinstance(response, bytes):
            # audio_np, sr = sf.read(io.BytesIO(response), dtype='int16') 

            def play():
                audio_np_test, samplerate = sf.read(io.BytesIO(response))
                import sounddevice as sd
                print(f"[CLIENT] Playing audio... (Sample rate: {samplerate}, Shape: {audio_np_test.shape})")
                print(f'samplerate {samplerate}')
                sd.play(audio_np_test, samplerate=samplerate)
                sd.wait()

            # await asyncio.to_thread(play)
            # await asyncio.sleep(7)

            audio = AudioSegment.from_file(io.BytesIO(response), format="wav")
            audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
            out = np.frombuffer(audio.raw_data, dtype=np.int16)
            return out

        else:
            print("[ERROR] Invalid response:", response)
            return np.zeros(16000, dtype=np.int16)  # 1s of silence fallback
