# Services

This directory contains the main services for the voice-translate system:

- `google_tts_service.py`: Text-to-speech using Google TTS.
- `google_translator_service.py`: Text translation using Google Translate.
- `deepgram_asr_service.py`: Speech recognition using Deepgram ASR.

## Usage Guide
- Each service implements a standard interface from `vpipe.capsules.services`.

## Notes
- Make sure to configure your Deepgram API key if you use the ASR service.
- All services support asynchronous (async) usage.
