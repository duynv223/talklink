import asyncio
import os
import tempfile
import numpy as np
import torch
from typing import Optional
from vpipe.capsules.services.tts import TTSServiceInterface
from services.openvoice.api import ToneColorConverter
from services.openvoice.se_extractor import get_se
# Try to import MeloTTS
try:
    from melo.api import TTS
    MELOTTS_AVAILABLE = True
except ImportError:
    MELOTTS_AVAILABLE = False
    print("Warning: MeloTTS not available. Install with: pip install melotts")


class OpenVoiceTTSService(TTSServiceInterface):
    """
    OpenVoice TTS Service that provides voice cloning capabilities.
    Uses MeloTTS as the base TTS model and OpenVoice for voice conversion.
    """
    
    def __init__(self, 
                 reference_speaker_path: str = "assets/vixtts_sample.wav",
                 converter_checkpoint_path: str = "model/openvoice/",
                 device: str = "cuda:0" if torch.cuda.is_available() else "cpu",
                 base_speaker: str = "EN",
                 speed: float = 1.0):
        """
        Initialize OpenVoice TTS Service.
        
        Args:
            reference_speaker_path: Path to the reference speaker audio file
            converter_checkpoint_path: Path to the OpenVoice converter checkpoint
            device: Device to run the model on ('cuda:0' or 'cpu')
            base_speaker: Base speaker to use for synthesis (e.g., 'EN', 'ZH', 'JP')
            speed: Speech synthesis speed multiplier
        """
        self.reference_speaker_path = reference_speaker_path
        self.converter_checkpoint_path = converter_checkpoint_path
        self.device = device
        self.base_speaker = base_speaker
        self.speed = speed
        
        # Initialize components
        self.tone_color_converter: Optional[ToneColorConverter] = None
        self.target_se: Optional[torch.Tensor] = None
        self.source_se: Optional[torch.Tensor] = None
        self.melotts_models: dict = {}  # Cache for MeloTTS models
        self._initialized = False
        
        # Language to MeloTTS language mapping
        self.lang_to_melotts = {
            'en': 'EN',
            'english': 'EN',
            'vi': 'EN',  # Vietnamese uses English base speaker
            'vietnamese': 'EN',
            'ja': 'JP',
            'japanese': 'JP',
            'zh': 'ZH',
            'chinese': 'ZH',
            'ko': 'KR',
            'korean': 'KR',
            'es': 'ES',
            'spanish': 'ES',
            'fr': 'FR',
            'french': 'FR'
        }
        
        # MeloTTS speaker mapping (default speakers for each language)
        self.melotts_speakers = {
            'EN': 'EN_NEWEST',  # Use newest English speaker
            'JP': 'JP',
            'ZH': 'ZH',
            'KR': 'KR',
            'ES': 'ES',
            'FR': 'FR'
        }
    
    async def start(self):
        """Initialize the OpenVoice TTS service."""
        if self._initialized:
            return
            
        if not MELOTTS_AVAILABLE:
            raise ImportError("MeloTTS not available. Install with: pip install melotts")
            
        # Initialize tone color converter
        config_path = os.path.join(self.converter_checkpoint_path, "converter", "config.json")
        checkpoint_path = os.path.join(self.converter_checkpoint_path, "converter", "checkpoint.pth")
        
        self.tone_color_converter = ToneColorConverter(config_path, device=self.device)
        self.tone_color_converter.load_ckpt(checkpoint_path)
        
        # Extract target speaker embedding
        self.target_se, _ = get_se(self.reference_speaker_path, self.tone_color_converter, vad=True)
        
        # Load base speaker embedding
        base_speaker_se_path = os.path.join(self.converter_checkpoint_path, "base_speakers", "ses", f"{self.base_speaker.lower()}.pth")
        if not os.path.exists(base_speaker_se_path):
            # Fallback to EN if specific speaker not found
            base_speaker_se_path = os.path.join(self.converter_checkpoint_path, "base_speakers", "ses", "en-us.pth")
            self.base_speaker = 'EN'
        
        self.source_se = torch.load(base_speaker_se_path, map_location=self.device)
        self._initialized = True
    
    async def stop(self):
        """Stop the OpenVoice TTS service."""
        self._initialized = False
        self.tone_color_converter = None
        self.target_se = None
        self.source_se = None
        self.melotts_models.clear()
    
    def _get_melotts_model(self, language: str) -> TTS:
        """Get or create MeloTTS model for the given language."""
        if language not in self.melotts_models:
            # Handle MPS backend issue for CPU
            if torch.backends.mps.is_available() and self.device == 'cpu':
                torch.backends.mps.is_available = lambda: False
            
            self.melotts_models[language] = TTS(language=language, device=self.device)
        
        return self.melotts_models[language]
    
    async def synthesize(self, text: str, lang: str) -> bytes:
        """
        Synthesize speech from text using OpenVoice voice cloning with MeloTTS.
        
        Args:
            text: Text to synthesize
            lang: Language code (e.g., 'en', 'vi', 'ja')
            
        Returns:
            bytes: Audio data as 16-bit PCM at 16kHz sample rate
        """
        if not self._initialized:
            raise RuntimeError("OpenVoice TTS Service not initialized. Call start() first.")
        
        if not text.strip():
            # Return silence for empty text
            return np.zeros(1600, dtype=np.int16).tobytes()
        
        try:
            # Determine MeloTTS language and speaker
            melotts_lang = self.lang_to_melotts.get(lang.lower(), 'EN')
            melotts_speaker = self.melotts_speakers.get(melotts_lang, 'EN_NEWEST')
            
            # Update source speaker embedding if needed
            if melotts_lang != self.base_speaker:
                base_speaker_se_path = os.path.join(self.converter_checkpoint_path, "base_speakers", "ses", f"{melotts_lang.lower()}.pth")
                if os.path.exists(base_speaker_se_path):
                    self.source_se = torch.load(base_speaker_se_path, map_location=self.device)
                    self.base_speaker = melotts_lang
            
            # Create temporary files for synthesis
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_src, \
                 tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                
                temp_src_path = temp_src.name
                temp_output_path = temp_output.name
            
            try:
                # Run synthesis in executor to avoid blocking
                loop = asyncio.get_running_loop()
                
                def _synthesize():
                    import soundfile as sf
                    
                    # Get MeloTTS model
                    model = self._get_melotts_model(melotts_lang)
                    
                    # Get speaker ID
                    speaker_ids = model.hps.data.spk2id
                    if melotts_speaker in speaker_ids:
                        speaker_id = speaker_ids[melotts_speaker]
                    else:
                        # Fallback to first available speaker
                        speaker_id = list(speaker_ids.values())[0]
                    
                    # Generate base speech using MeloTTS
                    model.tts_to_file(text, speaker_id, temp_src_path, speed=self.speed)
                    
                    # Apply voice conversion
                    if self.tone_color_converter is not None:
                        self.tone_color_converter.convert(
                            audio_src_path=temp_src_path,
                            src_se=self.source_se,
                            tgt_se=self.target_se,
                            output_path=temp_output_path,
                            tau=0.3,
                            message="@MyShell"
                        )
                    else:
                        # Fallback: just copy the source audio
                        import shutil
                        shutil.copy2(temp_src_path, temp_output_path)
                    
                    # Read the converted audio
                    converted_audio, sr = sf.read(temp_output_path)
                    
                    # Ensure correct format (16-bit, 16kHz, mono)
                    if len(converted_audio.shape) > 1:
                        converted_audio = converted_audio[:, 0]  # Convert to mono
                    
                    if sr != 16000:
                        # Resample if needed
                        import librosa
                        converted_audio = librosa.resample(converted_audio, orig_sr=sr, target_sr=16000)
                    
                    # Convert to 16-bit PCM
                    converted_audio = (converted_audio * 32767).astype(np.int16)
                    
                    return converted_audio
                
                audio_data = await loop.run_in_executor(None, _synthesize)
                
                # Convert to bytes
                return audio_data.tobytes()
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_src_path)
                    os.unlink(temp_output_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"Error in OpenVoice synthesis: {e}")
            # Return silence on error
            return np.zeros(1600, dtype=np.int16).tobytes()
    
    def set_reference_speaker(self, reference_speaker_path: str):
        """Update the reference speaker audio file."""
        self.reference_speaker_path = reference_speaker_path
        if self._initialized:
            # Re-initialize with new reference speaker
            asyncio.create_task(self.start())
    
    def set_speed(self, speed: float):
        """Set the speech synthesis speed."""
        self.speed = max(0.5, min(2.0, speed))  # Clamp between 0.5x and 2.0x
