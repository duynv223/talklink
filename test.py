import os
import torch
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Union
from enum import Enum
from dataclasses import dataclass
from services.openvoice import se_extractor
from services.openvoice.api import BaseSpeakerTTS, ToneColorConverter
from melo.api import TTS

import sys
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Language(Enum):
    ENGLISH_NEW = "EN_NEWEST"
    ENGLISH = "EN"
    SPANISH = "ES"
    FRENCH = "FR"
    CHINESE = "ZH"
    JAPANESE = "JP"
    KOREAN = "KR"

@dataclass
class TTSConfig:
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    output_dir: Union[str, Path] = Path("outputs")
    cache_dir: Union[str, Path] = Path("cache/speaker_embeddings")
    base_speakers_dir: Union[str, Path] = Path("checkpoints_v2/base_speakers/ses")
    converter_checkpoint_dir: Union[str, Path] = Path("checkpoints_v2/converter")
    default_speed: float = 1.0
    min_speed: float = 0.5
    max_speed: float = 2.0
    sample_rate: int = 24000
    default_message: str = "@MyShell"

class VoiceCloner:
    def __init__(self, config: TTSConfig, reference_speaker: Union[str, Path]):
        self.config = config
        self.reference_speaker = Path(reference_speaker)
        self._validate_paths()
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.device = config.device
        self.tone_converter = self._init_tone_converter()
        self.speaker_cache: Dict[str, torch.Tensor] = {}
        self.target_se = self._load_target_se()

    def _validate_paths(self):
        required_paths = {
            "converter_checkpoint_dir": self.config.converter_checkpoint_dir,
            "base_speakers_dir": self.config.base_speakers_dir,
            "reference_speaker": self.reference_speaker
        }
        for name, path in required_paths.items():
            if not Path(path).exists():
                raise FileNotFoundError(f"{name} path not found: {path}")
    def _init_tone_converter(self) -> ToneColorConverter:
        converter = ToneColorConverter(
            config_path=str(self.config.converter_checkpoint_dir / "config.json"),
            device=self.device
        )
        converter.load_ckpt(str(self.config.converter_checkpoint_dir / "checkpoint.pth"))
        return converter
    
    def _load_target_se(self) -> torch.Tensor:
        target_se, _ = se_extractor.get_se(
            audio_path=str(self.reference_speaker),
            vc_model=self.tone_converter,
            vad=True
        )
        return target_se
    
    def _get_speaker_embedding(self, speaker_id: str) -> torch.Tensor:
        speaker_key = speaker_id.lower().replace('_', '-')
        cache_path = Path(self.config.cache_dir) / f"{speaker_key}.pth"
        if speaker_key in self.speaker_cache:
            return self.speaker_cache[speaker_key]
        if cache_path.exists():
            embedding = torch.load(cache_path, map_location=self.device)
        else:
            source_path = self.config.base_speakers_dir / f"{speaker_key}.pth"
            embedding = torch.load(source_path, map_location=self.device)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(embedding, cache_path)
        self.speaker_cache[speaker_key] = embedding
        return embedding

class TTSEngine:
    def __init__(self, language: Language, voice_cloner: VoiceCloner):
        self.language = language
        self.cloner = voice_cloner
        self.speed = self.cloner.config.default_speed
        self.tts_model = TTS(language=language.value, device=self.cloner.device)
        self.speakers = {k.lower().replace('_', '-'): v for k, v in self.tts_model.hps.data.spk2id.items()}

    @property
    def available_speakers(self) -> list:
        return list(self.speakers.keys())

    def set_speed(self, speed: float):
        self.speed = max(min(speed, self.cloner.config.max_speed), self.cloner.config.min_speed)

    def generate_filename(self, text: str, speaker: str) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return self.cloner.output_dir / f"{timestamp}_{speaker}_{text_hash}.wav"

    def synthesize(self, text: str, speaker: Optional[str] = None, message: Optional[str] = None) -> Path:
        try:
            speaker = speaker or next(iter(self.speakers))
            if speaker not in self.speakers:
                raise ValueError(f"Invalid speaker: {speaker}. Available: {self.available_speakers}")

            speaker_id = self.speakers[speaker]
            temp_file = self.cloner.output_dir / "temp_input.wav"

            # Generate initial speech
            self.tts_model.tts_to_file(
                text,
                speaker_id,
                str(temp_file),
                self.speed
            )

            # Apply voice cloning
            output_path = self.generate_filename(text, speaker)
            source_se = self.cloner._get_speaker_embedding(speaker)

            self.cloner.tone_converter.convert(
                audio_src_path=str(temp_file),
                src_se=source_se,
                tgt_se=self.cloner.target_se,
                output_path=str(output_path),
                message=message or self.cloner.config.default_message
            )

            if temp_file.exists():
                temp_file.unlink()

            logger.info(f"Generated audio: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Synthesis failed: {str(e)}")
            raise RuntimeError(f"Voice synthesis error: {str(e)}") from e