import sounddevice as sd

def get_wasapi_index():
    hostapis = sd.query_hostapis()
    for idx, api in enumerate(hostapis):
        if "WASAPI" in api['name']:
            return idx
    raise RuntimeError("WASAPI not found on this system.")

def list_input_devices():
    """
    Result: List[Tuple[index, name]]
    """
    wasapi = get_wasapi_index()
    devices = sd.query_devices()
    result = []
    for idx, dev in enumerate(devices):
        if dev['hostapi'] == wasapi and dev['max_input_channels'] > 0:
            result.append((idx, dev['name']))
    return result

def list_output_devices():
    """
    Result: List[Tuple[index, name]]
    """
    wasapi = get_wasapi_index()
    devices = sd.query_devices()
    result = []
    for idx, dev in enumerate(devices):
        if dev['hostapi'] == wasapi and dev['max_output_channels'] > 0:
            result.append((idx, dev['name']))
    return result

def find_device_index(name, is_input=None):
    """
    Find the index of a device by name.
    If is_input = True: search only input devices.
    If is_input = False: search only output devices.
    If is_input = None: search all devices.
    """
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev['name'] == name:
            if is_input is True and dev['max_input_channels'] == 0:
                continue
            if is_input is False and dev['max_output_channels'] == 0:
                continue
            return idx
    raise ValueError(f"Device named '{name}' not found.")

if __name__ == "__main__":
    print("=== Input Devices (WASAPI) ===")
    for idx, name in list_input_devices():
        print(f"[{idx}] {name}")

    print("\n=== Output Devices (WASAPI) ===")
    for idx, name in list_output_devices():
        print(f"[{idx}] {name}")
