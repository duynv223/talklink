from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import uuid

@dataclass
class Payload:
    # uuid
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    # TimeStamp
    timestamp: float = field(default_factory=time.time)

    # Language
    src_lang: Optional[str] = None                  # ASR Transform updates this field
    dest_lang: Optional[str] = None                 # Translation Transform updates this field

    # ASR
    origin_text: Optional[str] = None               # ASR Transform updates this field
    origin_audio: Optional[bytearray] = None        # ASR Transform updates this field if have
    is_final: bool = False                          # ASR Transform updates this field                
    speaker: Optional[str] = None                   # ASR Transform updates this field if have

    # Translation
    translated_text: Optional[str] = None           # Translation Transform updates this field

    # TTS
    translated_audio: Optional[bytearray] = None    # Translation Transform updates this field

    # Direction
    direction: Optional[str] = None                 # 'Other' or 'You', used to determine the direction of the payload
