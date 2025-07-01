# fxtts

**Multilingual Text-to-Speech (TTS) Service using XTTS v2**

`fxtts` is a simple, extensible TTS server built upon Coqui's XTTS v2, supporting Vietnamese, English, and Japanese.

- **Vietnamese (`vi`)**: [`capleaft/vixtts`](https://huggingface.co/capleaf/viXTTS)
- **English & Japanese (`en`, `ja`)**: [`coqui/XTTS`](hhttps://huggingface.co/coqui/XTTS-v2)
- **Recommended Python version**: `3.11`

---

## Features

- Support for multiple languages via XTTS
- Ready-to-run TTS server
- Test client for quick interaction
- Modular structure for easy extension

---

### Installation

Follow the steps below to install and run the service.

### 1. Create and Activate Virtual Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

###  2. Clone and Install TTS Module
```
cd TTS
git clone git@github.com:thinhlpg/TTS.git
cd TTS
pip install -e .
```

### 3. Install Project Requirements
From the root directory of `fxtts`:
```
pip install -r requirements.txt
```

### 3. Install Project Requirements
```
python tts_server.py
```
Wait. You should see logs indicating the service is running on http://localhost:8765.

### 4. Running the Test Client
After the server is fully initialized, run:
```
python tests/tts_client.py
```
