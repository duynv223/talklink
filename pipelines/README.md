# Pipelines Overview

## 1. SpeechTranslator (`speech_translator.py`)
- **Function:** Receives audio input, converts it to text (ASR), translates the text, and synthesizes translated text to audio (TTS).
- **Flow:** (in) → ASR → Translation → TTS → (out)
- **Extra outputs:** ASR text (`asr_script`), translated text (`tran_script`).

## 2. AugmentedSpeechTranslator (`augmented_speech_translator.py`)
- **Function:** Extends the speech translation pipeline by mixing original and translated audio, and supports volume control for each stream.
- **Flow:** (in) → [SpeechTranslator → audio queue player] → [mixer(src)]
- **Mixer:** Mixes original and translated audio, allows adjusting the volume of each source.

## 3. DownStreamPipeline (`downstream_pipeline.py`)
- **Function:** Main application pipeline: receives audio from virtual speaker, processes translation, outputs to system speaker, and sends text to UI.
- **Flow:** (virtual speaker src) → AugmentedSpeechTranslator → (speaker sink)
- **Callback:** Sends ASR and translated text to the UI via callback.

## 4. UpStreamPipeline (`upstream_pipeline.py`)
T.B.D
