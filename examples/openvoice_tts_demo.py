import asyncio
import os
import sys
import soundfile as sf
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.openvoice_tts_service import OpenVoiceTTSService


async def main():
    tts_service = OpenVoiceTTSService(
        reference_speaker_path="assets/vixtts_sample.wav",
        converter_checkpoint_dir="model/openvoice/converter",
        base_speakers_dir="model/openvoice/base_speakers/ses",
        device="cuda:0" if torch.cuda.is_available() else "cpu"
    )
    
    try:
        await tts_service.start()
        print("✓ Service started successfully!")
        
        test_texts = [
            ("Hello, How are you? I'm fine, thank you. And you?", "EN"),
            ("Xin chào, em khoẻ không? Anh đứng đây từ chiều", "EN"),  # Vietnamese, but use EN model for demo
            ("こんにちは。お元気ですか？元気ですよ、ありがとうございます。あなたは？", "JP"),
            ("Bonjour, comment ça va? Je vais bien, merci!", "FR"),
            ("Hola, ¿cómo estás? Estoy bien, gracias.", "ES"),
            ("今天是个好天气。我们一起去散步吧！", "ZH"),
        ]
        
        os.makedirs("examples/output", exist_ok=True)
        
        for i, (text, lang) in enumerate(test_texts):
            print(f"\nLanguage: {lang}")
            speakers = tts_service.get_available_speakers(lang)
            print(f"Available speakers: {list(speakers.keys())}")
            speaker = next(iter(speakers)) if speakers else None
            print(f"Using speaker: {speaker}")
            
            try:
                audio_bytes = await tts_service.synthesize(
                    text, lang, speaker=speaker
                )
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                output_path = f"examples/output/openvoice_demo_{lang.lower()}_{i+1}.wav"
                sf.write(output_path, audio_data, 16000)
                print(f"✓ Audio saved to: {output_path}")
                print(f"  Duration: {len(audio_data) / 16000:.2f} seconds")
            except Exception as e:
                print(f"✗ Error synthesizing text {i+1} ({lang}): {e}")
        
        # Optionally, demonstrate using a custom reference speaker if you have another wav file
        custom_ref = "assets/vixtts_sample.wav"  # Replace with another file if available
        print("\nDemo: Custom reference speaker (if available)")
        try:
            audio_bytes = await tts_service.synthesize(
                "This is a custom voice clone demo.", "EN", reference_speaker_path=custom_ref
            )
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            output_path = f"examples/output/openvoice_demo_custom_ref.wav"
            sf.write(output_path, audio_data, 16000)
            print(f"✓ Audio saved to: {output_path}")
        except Exception as e:
            print(f"✗ Error with custom reference speaker: {e}")
        
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
    asyncio.run(main()) 