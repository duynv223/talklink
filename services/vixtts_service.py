import io
import asyncio
import numpy as np
import torch
import torchaudio
import os
import tempfile
from typing import Optional
from vpipe.capsules.services.tts import TTSServiceInterface

try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    from huggingface_hub import hf_hub_download, snapshot_download
    from underthesea import sent_tokenize
    from vinorm import TTSnorm
    XTTS_AVAILABLE = True
except ImportError as e:
    XTTS_AVAILABLE = False
    print(f"Warning: Required packages not available: {e}")
    print("Install with: pip install TTS huggingface_hub underthesea vinorm")


class ViXTTSService(TTSServiceInterface):
    def __init__(self, model_dir: Optional[str] = None, repo_id: str = "capleaf/viXTTS", 
                use_deepspeed: bool = False, device: str = "auto"):
        """
        Initialize ViXTTS service using Coqui TTS XTTS model.
        
        Args:
            model_dir: Path to the model directory. If None, will download from repo_id.
            repo_id: HuggingFace repository ID for the model.
            use_deepspeed: Whether to use DeepSpeed for faster inference.
            device: Device to run inference on ("auto", "cpu", "cuda")
        """
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), "..", "model")
        self.repo_id = repo_id
        self.use_deepspeed = use_deepspeed
        self.device = device
        self.model: Optional[Xtts] = None
        
        # Cache for conditioning latents (like in demo)
        self.conditioning_latents_cache = {}
        self.gpt_cond_latent = None
        self.speaker_embedding = None
        
        # Default reference audio path
        self.default_ref_audio = os.path.join(os.path.dirname(__file__), "..", "assets", "vixtts_sample.wav")
        
    async def start(self):
        """Initialize the ViXTTS model."""
        if not XTTS_AVAILABLE:
            raise ImportError("Required packages not available. Install TTS, huggingface_hub, underthesea, vinorm")
            
        loop = asyncio.get_running_loop()
        
        def init_model():
            # Clear GPU cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            os.makedirs(self.model_dir, exist_ok=True)
            
            # Check if model files exist, download if not
            required_files = ["model.pth", "config.json", "vocab.json", "speakers_xtts.pth"]
            files_in_dir = os.listdir(self.model_dir)
            
            if not all(file in files_in_dir for file in required_files):
                print(f"Downloading model from {self.repo_id}...")
                snapshot_download(
                    repo_id=self.repo_id,
                    repo_type="model",
                    local_dir=self.model_dir,
                )
                hf_hub_download(
                    repo_id="coqui/XTTS-v2",
                    filename="speakers_xtts.pth",
                    local_dir=self.model_dir,
                )
                print("Model download finished...")
            
            # Load model (exactly like in demo)
            xtts_config = os.path.join(self.model_dir, "config.json")
            config = XttsConfig()
            config.load_json(xtts_config)
            self.model = Xtts.init_from_config(config)
            
            print("Loading model...")
            self.model.load_checkpoint(
                config, checkpoint_dir=self.model_dir, use_deepspeed=self.use_deepspeed
            )
            
            # Move to device
            if self.device == "auto":
                if torch.cuda.is_available():
                    self.model.cuda()
            elif self.device == "cuda" and torch.cuda.is_available():
                self.model.cuda()
            
            print("Model Loaded!")
        
        await loop.run_in_executor(None, init_model)

    async def stop(self):
        """Clean up resources."""
        if self.model:
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self.model = None
            self.gpt_cond_latent = None
            self.speaker_embedding = None

    def _normalize_vietnamese_text(self, text: str) -> str:
        """Normalize Vietnamese text for better TTS quality (from demo)."""
        text = (
            TTSnorm(text, unknown=False, lower=False, rule=True)
            .replace("..", ".")
            .replace("!.", "!")
            .replace("?.", "?")
            .replace(" .", ".")
            .replace(" ,", ",")
            .replace('"', "")
            .replace("'", "")
            .replace("AI", "Ây Ai")
            .replace("A.I", "Ây Ai")
        )
        return text

    def _calculate_keep_len(self, text: str, lang: str) -> int:
        """Simple hack for short sentences"""
        if lang in ["ja", "zh-cn"]:
            return -1

        word_count = len(text.split())
        num_punct = text.count(".") + text.count("!") + text.count("?") + text.count(",")

        if word_count < 5:
            return 15000 * word_count + 2000 * num_punct
        elif word_count < 10:
            return 13000 * word_count + 2000 * num_punct
        return -1

    async def _get_conditioning_latents(self, reference_audio_path: str):
        """Get conditioning latents for reference audio (from demo)."""
        if not self.model:
            raise RuntimeError("Model not initialized. Call start() first.")
            
        # Check if conditioning latents are cached (like in demo)
        cache_key = (
            reference_audio_path,
            self.model.config.gpt_cond_len,
            self.model.config.max_ref_len,
            self.model.config.sound_norm_refs,
        )
        
        if cache_key in self.conditioning_latents_cache:
            print("Using conditioning latents cache...")
            self.gpt_cond_latent, self.speaker_embedding = self.conditioning_latents_cache[cache_key]
        else:
            print("Computing conditioning latents...")
            loop = asyncio.get_running_loop()
            
            def compute_latents():
                return self.model.get_conditioning_latents(
                    audio_path=reference_audio_path,
                    gpt_cond_len=self.model.config.gpt_cond_len,
                    max_ref_length=self.model.config.max_ref_len,
                    sound_norm_refs=self.model.config.sound_norm_refs,
                )
            
            self.gpt_cond_latent, self.speaker_embedding = await loop.run_in_executor(None, compute_latents)
            self.conditioning_latents_cache[cache_key] = (self.gpt_cond_latent, self.speaker_embedding)
            
    def set_reference_audio(self, reference_audio_path: str):
        """Set reference audio path"""
        self.default_ref_audio = reference_audio_path
        
    async def synthesize(self, text: str, lang: str) -> bytes:
        """
        Synthesize speech from text using ViXTTS (based on demo).
        
        Args:
            text: Text to synthesize
            lang: Language code (vi, en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh, hu, ko, ja)
            
        Returns:
            bytes: Audio data in 16-bit PCM format, 16kHz, mono
        """
        if not self.model:
            raise RuntimeError("ViXTTS model not initialized. Call start() first.")
            
        reference_audio_path = self.default_ref_audio
            
        # Get conditioning latents
        await self._get_conditioning_latents(reference_audio_path)
            
        loop = asyncio.get_running_loop()
        
        def synth():
            # Normalize text if Vietnamese (from demo)
            if lang == "vi":
                text_normalized = self._normalize_vietnamese_text(text)
            else:
                text_normalized = text
            
            # Split text by sentence (from demo)
            if lang in ["ja", "zh-cn"]:
                sentences = text_normalized.split("。")
            else:
                sentences = sent_tokenize(text_normalized)
            
            wav_chunks = []
            for sentence in sentences:
                if sentence.strip() == "":
                    continue
                    
                # Use exact same parameters as demo
                wav_chunk = self.model.inference(
                    text=sentence,
                    language=lang,
                    gpt_cond_latent=self.gpt_cond_latent,
                    speaker_embedding=self.speaker_embedding,
                    temperature=0.3,
                    length_penalty=1.0,
                    repetition_penalty=10.0,
                    top_k=30,
                    top_p=0.85,
                    enable_text_splitting=True,
                )
                
                keep_len = self._calculate_keep_len(sentence, lang)
                if keep_len > 0:
                    wav_chunk["wav"] = wav_chunk["wav"][:keep_len]
                
                wav_chunks.append(torch.tensor(wav_chunk["wav"]))
            
            if not wav_chunks:
                raise RuntimeError("No valid sentences to synthesize")
                
            out_wav = torch.cat(wav_chunks, dim=0).unsqueeze(0)
            
            # Convert to 16kHz mono 16-bit PCM
            if out_wav.shape[1] > 0:
                # Convert to mono if stereo
                if out_wav.shape[0] > 1:
                    out_wav = torch.mean(out_wav, dim=0, keepdim=True)
                
                # Resample from 24kHz to 16kHz
                resampler = torchaudio.transforms.Resample(24000, 16000)
                out_wav = resampler(out_wav)
                
                # Convert to int16
                out_wav = (out_wav * 32767).clamp(-32768, 32767).to(torch.int16)
                
                # Convert to numpy and then to bytes
                audio_array = out_wav.squeeze().numpy()
                return audio_array.tobytes()
            else:
                raise RuntimeError("Generated audio is empty")
        
        return await loop.run_in_executor(None, synth)