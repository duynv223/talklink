import asyncio
import websockets
import json
import io
import soundfile as sf
import torch 
import base64

from modules.tts_module import TTSModule
from modules.speaker_manager import SpeakerManager

MODELS = {
    "original_xtts": {
        "en": "coqui/XTTS-v2",
        "ja": "coqui/XTTS-v2",
        "vi": "capleaf/viXTTS"
    }, 
    "vixtts_xtts": {
        "en": "capleaf/viXTTS",
        "ja": "capleaf/viXTTS",
        "vi": "capleaf/viXTTS"
    }
}

ENABLE_VOICE_CLONING = True

def get_avail_device(): 
    if torch.cuda.is_available():
        device = "cuda"
    # elif torch.backends.mps.is_available() and platform.system() == "Darwin":
    #     device = "mps"  # Use Metal Performance Shaders on macOS
    else:
        device = "cpu"
    return device
class TTSServer:
    def __init__(self, host="localhost", port=8765, lang_to_model=MODELS["original_xtts"], device=None):
        self.host = host
        self.port = port
        self.default_speakers = {
            "vi": "ref/vi_male.wav",
            "en": "ref/en.wav",
            "ja": "ref/ja.wav"
        }
        self.tts = TTSModule(lang_to_model, device)
        self.speaker_manager = SpeakerManager(base_dir="speakers", min_duration_sec=6.0)

    def tensor_to_wav_bytes(self, wav_tensor, sample_rate=16000):
        buffer = io.BytesIO()
        if hasattr(wav_tensor, "detach"):
            wav_tensor = wav_tensor.squeeze().cpu().numpy()
        sf.write(buffer, wav_tensor, sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()
    
    def resolve_speaker_wav(self, speaker_id: str, lang: str, wav_b64: str = None):
        """Returns speaker reference path, saving it if valid. Falls back to default."""
        if speaker_id and wav_b64:
            try:
                wav_bytes = base64.b64decode(wav_b64)
                wav_np, sr = sf.read(io.BytesIO(wav_bytes), dtype='int16')
                if self.speaker_manager.save_reference(speaker_id, wav_np, sr):
                    print(f"[INFO] Saved reference voice for '{speaker_id}'")
                else:
                    print(f"[INFO] Reference too short or invalid for '{speaker_id}'")
            except Exception as e:
                print(f"[ERROR] Failed to decode/save reference for '{speaker_id}': {e}")

        if speaker_id:
            ref_path = self.speaker_manager.get_reference(speaker_id)
            if ref_path:
                return ref_path

        default_path = self.default_speakers.get(lang)
        print(f"[INFO] Using default speaker for lang='{lang}': {default_path}")
        return default_path

    async def handler(self, websocket):
        async for message in websocket:
            try:
                data = json.loads(message)
                lang = data.get("lang")
                text = data.get("text")
                speaker_id = data.get("speaker_id")
                wav_b64 = data.get("wav_bytes")

                print(f"[RECEIVED] text={text}, lang={lang}, speaker_id={speaker_id}")

                speaker_path = self.resolve_speaker_wav(speaker_id, lang, wav_b64)

                model = self.tts._get_model(lang)
                wav = model.synthesize(text, lang=lang, speaker_wav=speaker_path)
                wav_bytes_out = self.tensor_to_wav_bytes(wav)

                await websocket.send(wav_bytes_out)

            except Exception as e:
                error_msg = f"[ERROR] {str(e)}"
                await websocket.send(json.dumps({"error": error_msg}))
                print(error_msg)

    async def run(self):
        print(f"Starting TTS WebSocket server at ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port, max_size=None):
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8765
    model_type = "original_xtts" # original_xtts
    device = get_avail_device()
    server = TTSServer(host=host, port=port, lang_to_model=MODELS[model_type], device=device)
    asyncio.run(server.run())