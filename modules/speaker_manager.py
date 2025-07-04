from pathlib import Path
import soundfile as sf
import shutil
import time
import os
import numpy as np

class SpeakerManager:
    def __init__(self, base_dir="speakers", min_duration_sec=6.0):
        self.base_dir = Path(base_dir)
        self.min_duration_sec = min_duration_sec
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_speaker_dir(self, speaker_id):
        return self.base_dir / speaker_id

    def _get_ref_path(self, speaker_id):
        return self._get_speaker_dir(speaker_id) / "ref.wav"

    def _get_updated_at_path(self, speaker_id):
        return self._get_speaker_dir(speaker_id) / "updated_at.txt"
    
    def _get_raw_path(self, speaker_id):
        return self._get_speaker_dir(speaker_id) / "raw_input.wav"

    def save_reference(self, speaker_id, wav, sample_rate=16000):
        duration = len(wav) / sample_rate
        if duration < self.min_duration_sec:
            print(f"[INFO] Skipped saving reference for {speaker_id}: too short ({duration:.2f}s)")
            return False
        
        speaker_dir = self._get_speaker_dir(speaker_id)
        speaker_dir.mkdir(parents=True, exist_ok=True)
        ref_path = self._get_ref_path(speaker_id)

        # Convert stereo to mono
        if wav.ndim == 2:
            wav = wav.mean(axis=1)

        # Handle int16 input (normalize to float32)
        if wav.dtype == np.int16:
            wav = wav.astype(np.float32) / 32768.0

        # Optional: normalize volume
        if np.max(np.abs(wav)) > 0:
            wav = wav / np.max(np.abs(wav))

        # Save clean WAV
        sf.write(str(ref_path), wav, sample_rate, format="WAV", subtype="PCM_16")
        print(f"[SAVED] Speaker '{speaker_id}' reference saved: {ref_path}")
        print(f"        Duration: {duration:.2f}s, Sample rate: {sample_rate}, Max: {np.max(np.abs(wav)):.3f}")

        with open(self._get_updated_at_path(speaker_id), "w") as f:
            f.write(str(int(time.time())))
        return True

    def get_reference(self, speaker_id):
        """Return path to the speaker reference voice if exists"""
        ref_path = self._get_ref_path(speaker_id)
        if ref_path.exists():
            return str(ref_path)
        return None

    def has_valid_reference(self, speaker_id):
        """Check if speaker has a valid reference voice"""
        return self._get_ref_path(speaker_id).exists()

    def cleanup_old_speakers(self, days_threshold=7):
        """Remove speaker directories not updated in given days"""
        now = time.time()
        threshold = days_threshold * 86400

        for speaker_dir in self.base_dir.iterdir():
            if not speaker_dir.is_dir():
                continue
            updated_path = speaker_dir / "updated_at.txt"
            if not updated_path.exists():
                shutil.rmtree(speaker_dir)
                continue
            try:
                with open(updated_path) as f:
                    updated_time = int(f.read().strip())
                if now - updated_time > threshold:
                    shutil.rmtree(speaker_dir)
            except Exception:
                shutil.rmtree(speaker_dir)

