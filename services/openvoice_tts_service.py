import os
import torch
import tempfile
import numpy as np
from vpipe.capsules.services.tts import TTSServiceInterface
from services.openvoice.api import ToneColorConverter
from services.openvoice.se_extractor import get_se
try:
    from melo.api import TTS
    MELOTTS_AVAILABLE = True
except ImportError:
    MELOTTS_AVAILABLE = False

class OpenVoiceTTSService(TTSServiceInterface):
    def __init__(self,
                reference_speaker_path="assets/vixtts_sample.wav",
                converter_checkpoint_dir="model/openvoice/converter",
                base_speakers_dir="model/openvoice/base_speakers/ses",
                device=None,
                speed=1.0):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.reference_speaker_path = reference_speaker_path
        self.converter_checkpoint_dir = converter_checkpoint_dir
        self.base_speakers_dir = base_speakers_dir
        self.speed = speed
        self.tts_model = None
        self.tone_converter = None
        self.target_se = None
        self.speaker_cache = {}
        self._initialized = False

    async def start(self):
        if self._initialized:
            return
        if not MELOTTS_AVAILABLE:
            raise ImportError("MeloTTS not available. Install with: pip install melotts")
        # Init tone converter
        config_path = os.path.join(self.converter_checkpoint_dir, "config.json")
        checkpoint_path = os.path.join(self.converter_checkpoint_dir, "checkpoint.pth")
        self.tone_converter = ToneColorConverter(config_path=config_path, device=self.device)
        self.tone_converter.load_ckpt(checkpoint_path)
        # Extract target speaker embedding
        self.target_se, _ = get_se(self.reference_speaker_path, self.tone_converter, vad=True)
        # Init MeloTTS (English only for simplicity)
        self.tts_model = TTS(language="EN_NEWEST", device=self.device)
        self.speakers = {k.lower().replace('_', '-'): v for k, v in self.tts_model.hps.data.spk2id.items()}
        self._initialized = True

    async def stop(self):
        self._initialized = False
        self.tone_converter = None
        self.target_se = None
        self.tts_model = None
        self.speaker_cache.clear()

    def _get_speaker_embedding(self, speaker_key):
        key = speaker_key.lower().replace('_', '-')
        if key in self.speaker_cache:
            return self.speaker_cache[key]
        path = os.path.join(self.base_speakers_dir, f"{key}.pth")
        emb = torch.load(path, map_location=self.device)
        self.speaker_cache[key] = emb
        return emb

    async def synthesize(self, text: str, lang: str) -> bytes:
        if not self._initialized or self.tts_model is None or self.tone_converter is None:
            raise RuntimeError("OpenVoiceTTSService not initialized. Call start() first.")
        if not text.strip():
            return np.zeros(1600, dtype=np.int16).tobytes()
        # Use first available speaker for simplicity
        speaker = next(iter(self.speakers))
        speaker_id = self.speakers[speaker]
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_src, \
            tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_out:
            temp_src_path = temp_src.name
            temp_out_path = temp_out.name
        try:
            # Synthesize with MeloTTS
            self.tts_model.tts_to_file(text, speaker_id, temp_src_path, self.speed)
            # Voice conversion
            source_se = self._get_speaker_embedding(speaker)
            self.tone_converter.convert(
                audio_src_path=temp_src_path,
                src_se=source_se,
                tgt_se=self.target_se,
                output_path=temp_out_path,
                message="@MyShell"
            )
            import soundfile as sf
            audio, sr = sf.read(temp_out_path)
            if len(audio.shape) > 1:
                audio = audio[:, 0]
            if sr != 16000:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            audio = (audio * 32767).astype(np.int16)
            return audio.tobytes()
        finally:
            try:
                os.unlink(temp_src_path)
                os.unlink(temp_out_path)
            except Exception:
                pass
