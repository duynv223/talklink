import io
from gtts import gTTS
from pydub import AudioSegment
import asyncio
import numpy as np
from vpipe.capsules.services.tts import TTSServiceInterface

class GoogleTTSService(TTSServiceInterface):
    def __init__(self, settings={}):
        pass
    
    async def start(self):
        pass

    async def stop(self):
        pass

    async def synthesize(self, text: str, lang: str, ref_voice: bytearray, speaker_id: str) -> bytes:
        loop = asyncio.get_running_loop()
        buf = io.BytesIO()

        def synth():
            tts = gTTS(text=text, lang=lang)
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf

        buf = await loop.run_in_executor(None, synth)
        audio = AudioSegment.from_file(buf, format="mp3")
        audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
        out = np.frombuffer(audio.raw_data, dtype=np.int16)
        return out
