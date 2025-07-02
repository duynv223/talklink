# Speech Translator Application
Note: Currently using self talk mode as the main demo pipeline. This means the app records from your default microphone and plays back to your default system speaker.
Use downstream or upstream pipelines later.

## Project structure
```
vpipe/
    core/ (core pipeline logic)
    capsules/
pipelines/
    augmented_speech_translator.py
    downstream_pipeline.py
    selftalk_pipeline.py
    speech_translator.py
assets/
tests/
examples/
    audio_mixer.py         # Run audio mixing pipeline
    hello_vpipe.py         # Minimal pipeline example
    selftalk.py            # Self-talk pipeline demo
    
services/
    deepgram_asr_service.py
    google_translator_service.py
    google_tts_service.py
app/
    assets/
    controller/
    models/
    qml/
main.py
requirements.txt
```

## Installation
```bash
python -m venv .venv # recommend python 3.11
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
```bash
# precondition: Register and get api key from Deepgram
# on venv shell
$env:DEEPGRAM_API_KEY="your-deepgram-api-key"
python main.py
```

## Completed Tasks

- **Pipeline Framework (`vpipe`)**
    - Core pipeline logic
    - Capsule definitions (support downstream)
- **Services (Cloud-based)**
    - ASR (Deepgram)
    - Translation (Google Translate)
    - TTS (Google TTS)
- **Pipelines**
    - Downstream pipeline
    - Self-talk pipeline
- **Application (Qt)**
    - Support Start/Stop translator
    - Support conversation list
    - Support changing language  and mixer settings
    - Display status of translator

## Todo Tasks

- **Services**
    - [x] ASR service
    - [x] Translation service
    - [x] TTS service
- **Application**
    - [x] Upstream pipeline
    - [x] Settings
        - [x] Upstream/downstream controls
        - [x] Audio device selector
        - [x] Synthesis speed
    - [x] Implement setting manager
    - [ ] Audio signal visualization
    - [ ] Conversation list readability
    - [ ] New conversation/history
    - [ ] List/read saved conversations
    - [x] System messages
    - [ ] Modes
        - [x] Conference (virtual mic/speaker)
        - [ ] Self Talk (system mic/speaker)
    - [x] Advanced: model/service selection
    - [x] Error/warning notifications
    - [ ] App icon/logo
    - [x] Fix to remove warning console log
- **Pipelines**
    - [x] Logging
    - [ ] Capsule error handler
    - [ ] Flush event
    - [ ] Interface profile/validator
    - [ ] Input/output buffer


