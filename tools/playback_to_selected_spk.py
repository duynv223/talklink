import time
import sounddevice as sd
import numpy as np
from pydub import AudioSegment
import sys


def list_wasapi_stereo_output_devices(channels=2):
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    default_output = sd.default.device[1]
    output_devices = [
        (i, d, hostapis[d['hostapi']]['name'])
        for i, d in enumerate(devices)
        if d['max_output_channels'] == channels and 'wasapi' in hostapis[d['hostapi']]['name'].lower()
    ]
    output_devices.sort(key=lambda x: x[0] != default_output)
    return output_devices, default_output


def select_output_device_interactive(output_devices, default_output):
    if not output_devices:
        print("No suitable output devices found.")
        return None

    print("Available WASAPI stereo output devices:")
    for idx, (dev_idx, d, hostapi_name) in enumerate(output_devices):
        default_tag = " [default]" if dev_idx == default_output else ""
        print(f"{idx}: [{dev_idx}] {d['name']} ({hostapi_name}){default_tag}")

    while True:
        try:
            sel = int(input("Select output device index in this list: "))
            if 0 <= sel < len(output_devices):
                dev_idx, d, hostapi_name = output_devices[sel]
                print(f"Selected device: [{dev_idx}] {d['name']} ({hostapi_name})")
                return dev_idx
        except Exception:
            pass
        print("Invalid selection. Try again.")


def play_audio_to_device(samples, output_device, sample_rate, channels, chunk_size):
    total_frames = samples.shape[0]
    frames_per_chunk = chunk_size // channels
    print(f"Playing to output device index {output_device} ...")
    stream = sd.OutputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype='float32',
        blocksize=frames_per_chunk,
        device=output_device
    )
    stream.start()
    idx = 0
    try:
        while idx < total_frames:
            chunk = samples[idx:idx+frames_per_chunk]
            stream.write(chunk)
            idx += frames_per_chunk
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        stream.stop()
        stream.close()
    print("Done.")

def load_audio_file(mp3_file, sample_rate, channels):
    audio = AudioSegment.from_file(mp3_file)
    audio = audio.set_frame_rate(sample_rate)
    audio = audio.set_channels(channels)
    audio = audio.set_sample_width(2)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
    samples = samples.reshape((-1, channels))
    return samples

def main():
    sample_rate = 48000
    channels = 2
    chunk_size = 4096
    if len(sys.argv) > 1:
        mp3_file = sys.argv[1]
    else:
        mp3_file = input("Enter path to mp3 file: ").strip()
        
    output_devices, default_output = list_wasapi_stereo_output_devices(channels)
    output_device = select_output_device_interactive(output_devices, default_output)
    samples = load_audio_file(mp3_file, sample_rate, channels)
    play_audio_to_device(samples, output_device, sample_rate, channels, chunk_size)

if __name__ == "__main__":
    main()
