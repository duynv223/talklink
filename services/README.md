# Services

This directory contains the main services for the voice-translate system:

- `google_tts_service.py`: Text-to-speech using Google TTS.
- `google_translator_service.py`: Text translation using Google Translate.
- `deepgram_asr_service.py`: Speech recognition using Deepgram ASR.

## How to add a new service
1. **Create a new Python file** in this directory (e.g. `my_service.py`).
2. **Implement the appropriate interface** (`ASRServiceInterface`, `TTSServiceInterface`, etc.) from `vpipe.capsules.services`.
3. **Add your service to the config** (see `services_config.yaml`):
   - Specify `id`, `class`, and `schema` path for your service.
4. **Create a schema YAML** for your service settings (see other services for examples).
   - All service settings will be passed to your service's constructor via `**kwargs` when the service is created.
   - Example:
     ```python
     class MyService(SomeServiceInterface):
         def __init__(self, *args, **kwargs):
             # Access settings from kwargs
             my_setting = kwargs.get('my_setting')
             ...
     ```
5. **(Optional) Update the UI** if your service needs custom settings or display.
6. **Test your service** by selecting it in the app and verifying functionality.

> **Note:** You can change service settings directly in the app via the Settings tab.
