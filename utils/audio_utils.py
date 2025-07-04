# utils/audio_utils.py
import numpy as np
import noisereduce as nr
import io
import soundfile as sf

def denoise_audio(wav_np, sr):
    return nr.reduce_noise(y=wav_np, sr=sr)

def get_audio_duration(wav_np, sr):
    return len(wav_np) / sr

