import sounddevice as sd
import numpy as np

SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2  # bytes per sample (16-bit PCM)
CHUNK_SIZE = 4096

def list_devices(direction='input', channels=2):
    """
    direction: 'input' or 'output'
    """
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    key = 'max_input_channels' if direction == 'input' else 'max_output_channels'
    filtered = [
        (i, d, hostapis[d['hostapi']]['name'])
        for i, d in enumerate(devices)
        if d[key] >= channels and 'wasapi' in hostapis[d['hostapi']]['name'].lower()
    ]
    return filtered

def select_device_auto(devices, device_type='input'):
    for dev_idx, d, hostapi_name in devices:
        if 'ns team' in d['name'].lower():
            print(f"Auto-selected {device_type} device: [{dev_idx}] {d['name']} ({hostapi_name})")
            return dev_idx
    # fallback to manual selection
    print(f"No {device_type} device with 'NS Team' found. Please select manually.")
    for idx, (dev_idx, d, hostapi_name) in enumerate(devices):
        print(f"{idx}: [{dev_idx}] {d['name']} ({hostapi_name})")
    while True:
        try:
            sel = int(input(f"Select {device_type} device index in this list: "))
            if 0 <= sel < len(devices):
                dev_idx, d, hostapi_name = devices[sel]
                print(f"Selected device: [{dev_idx}] {d['name']} ({hostapi_name})")
                return dev_idx
        except Exception:
            pass
        print("Invalid selection. Try again.")

def main():
    input_devices = list_devices('input', CHANNELS)
    if not input_devices:
        print("No suitable input devices found.")
        return
    input_device = select_device_auto(input_devices, 'input')

    output_devices = list_devices('output', CHANNELS)
    if not output_devices:
        print("No suitable output devices found.")
        return
    output_device = select_device_auto(output_devices, 'output')

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        # indata: float32 [-1,1]
        arr = np.clip(indata, -1, 1)
        arr = (arr * 32767).astype(np.int16)
        stream_out.write(arr)
        print(".", end="", flush=True)

    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16',
        blocksize=CHUNK_SIZE // (CHANNELS * SAMPLE_WIDTH),
        device=output_device
    ) as stream_out:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype='float32',
            blocksize=CHUNK_SIZE // (CHANNELS * SAMPLE_WIDTH),
            device=input_device,
            callback=callback
        ):
            print("Looping audio from real mic to real speaker. Press Ctrl+C to stop.")
            try:
                while True:
                    sd.sleep(1000)
            except KeyboardInterrupt:
                print("\nStopped by user.")

if __name__ == "__main__":
    main()
