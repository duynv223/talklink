import time
import sounddevice as sd
import numpy as np

from virtual_audio_device_client import VirtualAudioDeviceClient

def grab(vspk, stream, sample_rate, channels, sample_width, chunk_size):
    try:
        while True:
            try:
                data = vspk.read(chunk_size)
                if not data: raise Exception("No data read from virtual mic")
                print(".", end="", flush=True)
            except Exception:
                time.sleep(0.01)
                continue

            arr = np.frombuffer(data, dtype=np.int16)
            arr = arr.reshape(-1, channels)
            stream.write(arr)

    except KeyboardInterrupt:
        print("Stopped by user.")

def main():
    SAMPLE_RATE = 48000
    CHANNELS = 2
    SAMPLE_WIDTH = 2 # vspeaker uses 16-bit samples
    CHUNK_SIZE = 4096

    with VirtualAudioDeviceClient() as vspk:
        with sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='int16',
            blocksize=CHUNK_SIZE // (CHANNELS * SAMPLE_WIDTH)
        ) as stream:
            stream.start()
            grab(vspk, stream, SAMPLE_RATE, CHANNELS, SAMPLE_WIDTH, CHUNK_SIZE)

if __name__ == "__main__":
    main()
