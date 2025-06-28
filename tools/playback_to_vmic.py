"""
Stream an audio file to the virtual microphone device in real time, chunk by chunk.
"""

from pydub import AudioSegment
import time
from virtual_audio_device_client import VirtualAudioDeviceClient

def load_audio(filename):
    audio = AudioSegment.from_mp3(filename) \
        .set_channels(2) \
        .set_frame_rate(48000) \
        .set_sample_width(4)
    return audio.raw_data

def play_audio_to_vmic(client, audio_bytes):
    chunk_size = 480 * 4 * 2  # 10ms chunk
    chunk_duration_sec = chunk_size / (48000 * 4 * 2)
    total_chunks = (len(audio_bytes) + chunk_size - 1) // chunk_size

    start_time = time.time()
    for i, offset in enumerate(range(0, len(audio_bytes), chunk_size)):
        chunk = audio_bytes[offset:offset + chunk_size]
        target_time = start_time + i * chunk_duration_sec

        try:
            client.write(chunk)
            print(f"\rChunk {i+1}/{total_chunks}", end="", flush=True)
        except Exception as e:
            print(f"\nError writing chunk {i}: {e}")

        sleep_time = target_time + chunk_duration_sec - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
    print()

def main():
    import sys
    if len(sys.argv) > 1:
        mp3_file = sys.argv[1]
    else:
        mp3_file = input("Enter path to mp3 file: ").strip()

    print("Opening device")
    with VirtualAudioDeviceClient() as client:
        audio_bytes = load_audio(mp3_file)
        client.clear_mic()
        play_audio_to_vmic(client, audio_bytes)

if __name__ == "__main__":
    main()
