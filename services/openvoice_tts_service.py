import os
import torch
import tempfile
import numpy as np
from typing import Optional, Dict
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
        self.default_reference_speaker_path = reference_speaker_path
        self.converter_checkpoint_dir = converter_checkpoint_dir
        self.base_speakers_dir = base_speakers_dir
        self.speed = speed
        self.tts_models: Dict[str, TTS] = {}  # language -> TTS model
        self.tone_converter = None
        self.target_se_cache: Dict[str, torch.Tensor] = {}  # ref path -> embedding
        self.speaker_cache: Dict[str, torch.Tensor] = {}  # speaker key -> embedding
        self.speakers: Dict[str, int] = {}  # last loaded speakers
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
        self._initialized = True

    async def stop(self):
        self._initialized = False
        self.tone_converter = None
        self.tts_models.clear()
        self.target_se_cache.clear()
        self.speaker_cache.clear()
        self.speakers.clear()

    def _get_tts_model(self, lang: str) -> TTS:
        lang_key = lang.upper()
        if lang_key not in self.tts_models:
            self.tts_models[lang_key] = TTS(language=lang_key, device=self.device)
        # Update speakers dict for this model
        self.speakers = {k.lower().replace('_', '-'): v for k, v in self.tts_models[lang_key].hps.data.spk2id.items()}
        return self.tts_models[lang_key]

    def _get_target_se(self, reference_speaker_path: str) -> torch.Tensor:
        if reference_speaker_path in self.target_se_cache:
            return self.target_se_cache[reference_speaker_path]
        target_se, _ = get_se(reference_speaker_path, self.tone_converter, vad=True)
        self.target_se_cache[reference_speaker_path] = target_se
        return target_se

    def _get_speaker_embedding(self, speaker_key: str) -> torch.Tensor:
        key = speaker_key.lower().replace('_', '-')
        if key in self.speaker_cache:
            return self.speaker_cache[key]
        path = os.path.join(self.base_speakers_dir, f"{key}.pth")
        emb = torch.load(path, map_location=self.device)
        self.speaker_cache[key] = emb
        return emb

    async def synthesize(self, text: str, lang: str, speaker: Optional[str] = None, reference_speaker_path: Optional[str] = None) -> bytes:
        """
        Synthesize speech from text using OpenVoice voice cloning with MeloTTS.
        Args:
            text: Text to synthesize
            lang: Language code (e.g., 'en', 'vi', 'ja', 'zh', etc.)
            speaker: Speaker key (optional, default: first available)
            reference_speaker_path: Path to reference audio for voice cloning (optional, default: initial reference)
        Returns:
            bytes: Audio data as 16-bit PCM at 16kHz sample rate
        """
        if not self._initialized or self.tone_converter is None:
            raise RuntimeError("OpenVoiceTTSService not initialized. Call start() first.")
        if not text.strip():
            return np.zeros(1600, dtype=np.int16).tobytes()
        # Get TTS model for language
        tts_model = self._get_tts_model(lang)
        # Get speakers for this model
        speakers = self.speakers
        # Pick speaker
        speaker_key = speaker or next(iter(speakers))
        if speaker_key not in speakers:
            raise ValueError(f"Invalid speaker: {speaker_key}. Available: {list(speakers.keys())}")
        speaker_id = speakers[speaker_key]
        # Get reference speaker embedding
        ref_path = reference_speaker_path or self.default_reference_speaker_path
        target_se = self._get_target_se(ref_path)
        # Get base speaker embedding for conversion
        source_se = self._get_speaker_embedding(speaker_key)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_src, \
             tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_out:
            temp_src_path = temp_src.name
            temp_out_path = temp_out.name
        try:
            # Synthesize with MeloTTS
            tts_model.tts_to_file(text, speaker_id, temp_src_path, self.speed)
            # Voice conversion
            self.tone_converter.convert(
                audio_src_path=temp_src_path,
                src_se=source_se,
                tgt_se=target_se,
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

    def get_available_speakers(self, lang: str) -> Dict[str, int]:
        """Return available speakers for a given language."""
        tts_model = self._get_tts_model(lang)
        return {k.lower().replace('_', '-'): v for k, v in tts_model.hps.data.spk2id.items()}
