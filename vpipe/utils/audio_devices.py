import sounddevice as sd

"""
todo: fix device query is not updated when devices are added/removed
"""
def default_input_filter(name, dev):
    ingore_keys = ['virtual audio', 'sound mapper']
    return (
        dev.get('hostapi', -1) == sd.default.hostapi
        and dev.get('max_input_channels', 0) > 0
        and (not any(k in name.lower() for k in ingore_keys))
    )


def default_output_filter(name, dev):
    ingore_keys = ['virtual audio', 'sound mapper']
    return (
        dev.get('hostapi', -1) == sd.default.hostapi
        and dev.get('max_output_channels', 0) > 0
        and (not any(k in name.lower() for k in ingore_keys))
    )


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

    import sounddevice as sd

    info = sd.query_devices()
    default_hostapi_index = sd.default.hostapi
    hostapi_info = sd.query_hostapis(default_hostapi_index)

    print("Host API mặc định:", hostapi_info['name'])

