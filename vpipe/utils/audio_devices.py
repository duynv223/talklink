import sounddevice as sd

"""
Default, we exclude "NS Team" virtual devices
"""

def default_input_filter(name, dev):
    return (
        dev.get('hostapi', -1) == get_wasapi_index()
        and dev.get('max_input_channels', 0) > 0
        and (not 'ns team' in name.lower())
    )


def default_output_filter(name, dev):
    return (
        dev.get('hostapi', -1) == get_wasapi_index()
        and dev.get('max_output_channels', 0) > 0
        and (not 'ns team' in name.lower())
    )


def get_wasapi_index():
    hostapis = sd.query_hostapis()
    for idx, api in enumerate(hostapis):
        if "WASAPI" in api['name']:
            return idx
    raise RuntimeError("WASAPI not found on this system.")


def list_input_devices(filter=None):
    """
    Returns: List[Tuple[index, name]]
    filter: callback(name:str, dev:dict)->bool, if provided, will be used to filter devices
    """
    if filter is None:
        filter = default_input_filter
    devices = sd.query_devices()
    result = []
    for idx, dev in enumerate(devices):
        if filter is None or filter(dev['name'], dev):
            result.append((idx, dev['name']))
    return result


def list_output_devices(filter=None):
    """
    Returns: List[Tuple[index, name]]
    filter: callback(name:str, dev:dict)->bool, if provided, will be used to filter devices
    """
    if filter is None:
        filter = default_output_filter
    devices = sd.query_devices()
    result = []
    for idx, dev in enumerate(devices):
        if filter is None or filter(dev['name'], dev):
            result.append((idx, dev['name']))
    return result


def find_device_index(name, is_input=None, filter=None):
    """
    Find the index of a device by name.
    If is_input = True: search only input devices.
    If is_input = False: search only output devices.
    If is_input = None: search all devices.
    filter: callback(name:str, dev:dict)->bool, if provided, will be used to filter devices
    """
    if is_input is True and filter is None:
        filter = default_input_filter
    if is_input is False and filter is None:
        filter = default_output_filter
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if filter is not None and not filter(dev['name'], dev):
            continue
        if dev['name'] == name:
            return idx
    raise ValueError(f"Device named '{name}' not found.")


if __name__ == "__main__":
    print(">> Input Devices (WASAPI)")
    for idx, name in list_input_devices():
        print(f"[{idx}] {name}")

    print("\n>> Output Devices (WASAPI)")
    for idx, name in list_output_devices():
        print(f"[{idx}] {name}")
