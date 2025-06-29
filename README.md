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
    - [ ] ASR service
    - [ ] Translation service
    - [ ] TTS service
- **Application**
    - [x] Upstream pipeline
    - [o] Settings
        - [x] Upstream/downstream controls
        - [ ] Audio device selector
        - [ ] Synthesis speed
    - [x] Implement setting manager
    - [ ] Audio signal visualization
    - [ ] Conversation list readability
    - [ ] New conversation/history
    - [ ] System messages
    - [ ] Modes
        - [x] Conference (virtual mic/speaker)
        - [ ] Self Talk (system mic/speaker)
    - [ ] List/read saved conversations
    - [ ] Advanced: model/service selection
    - [ ] Error/warning notifications
    - [ ] App icon/logo
    - [ ] Fix to remove warning console log
- **Pipelines**
    - [ ] Logging
    - [ ] Capsule error handler
    - [ ] Flush event
    - [ ] Interface profile/validator
    - [ ] Input/output buffer


