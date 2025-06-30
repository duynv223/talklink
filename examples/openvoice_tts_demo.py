import asyncio
import os
import sys
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.openvoice_tts_service import OpenVoiceTTSService


async def main():
    tts_service = OpenVoiceTTSService(
        reference_speaker_path="assets/vixtts_sample.wav",
        converter_checkpoint_path="model/openvoice/",
        device="cuda:0" if torch.cuda.is_available() else "cpu"
    )
    
    try:
        await tts_service.start()
        print("✓ Service started successfully!")
        
        test_texts = [
            ("Hello, How are you? I'm fine, thank you. And you?", "en"),
            ("Xin chào, em khoẻ không? Anh đứng đâ từ chiều", "vi"),
            ("こんにちは。お元気ですか？元気ですよ、ありがとうございます。あなたは？", "ja"),
        ]
        
        os.makedirs("examples/output", exist_ok=True)
        
        for i, (text, lang) in enumerate(test_texts):
            print(f"\nSynthesizing text {i+1} ({lang}): {text}")
            
            try:
                audio_bytes = await tts_service.synthesize(text, lang)
                
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                
                output_path = f"examples/output/openvoice_demo_{lang}_{i+1}.wav"
                sf.write(output_path, audio_data, 16000)
                
                print(f"✓ Audio saved to: {output_path}")
                print(f"  Duration: {len(audio_data) / 16000:.2f} seconds")
                
            except Exception as e:
                print(f"✗ Error synthesizing text {i+1}: {e}")
        
        print("\n" + "=" * 50)
        print("Demo completed! Check the 'examples/output' directory for generated audio files.")
        
    except Exception as e:
        print(f"✗ Failed to start service: {e}")
        if "MeloTTS not available" in str(e):
            print("\nTo install MeloTTS, run: pip install melotts")
    finally:
        await tts_service.stop()


if __name__ == "__main__":
    import torch
    import numpy as np
    asyncio.run(main()) 