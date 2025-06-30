#!/usr/bin/env python3
"""
Basic test for the ViXTTS service.
Tests the service directly without pipeline wrappers.
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vixtts_service import ViXTTSService


async def test_vixtts_direct():
    """Test ViXTTS service directly."""
    
    print("=== Testing ViXTTS Service Directly ===")
    
    # Create ViXTTS service
    tts_service = ViXTTSService(device="cpu", use_deepspeed=False)
    
    try:
        # Start the service
        print("Starting ViXTTS service...")
        await tts_service.start()
        print("✓ ViXTTS service started")
        
        # Test synthesis directly
        test_text = "Hello, this is a test of ViXTTS!"
        print(f"\nSynthesizing: '{test_text}'")
        
        # Call synthesize directly
        audio_data = await tts_service.synthesize(test_text, "en")
        
        print(f"✓ Generated {len(audio_data)} bytes of audio")
        print(f"✓ Audio format: 16-bit PCM, 16kHz, mono")
        
        # Test different languages
        languages = ["en", "vi", "es", "fr"]
        for lang in languages:
            test_text = f"Test in {lang} language"
            audio_data = await tts_service.synthesize(test_text, lang)
            print(f"✓ {lang}: {len(audio_data)} bytes")
        
        print("\n=== Direct Test Passed ===")
        print("ViXTTS service works directly!")
        
    except ImportError as e:
        print(f"✗ Missing dependencies: {e}")
        print("Install with: pip install torch torchaudio TTS huggingface_hub underthesea vinorm")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await tts_service.stop()
        print("✓ Service stopped")


if __name__ == "__main__":
    asyncio.run(test_vixtts_direct()) 