import win32file
import win32con
import struct

import logging
logger = logging.getLogger(__name__)


class VirtualAudioDeviceClient:
    """
    Client for writing audio data to a Windows virtual microphone device.
    Supports write, clear, and buffer status operations.
    """

    DEFAULT_DEVICE_PATH = r'\\.\VirtualAudio'
    IOCTL_VIRTUALAUDIO_BASE = 0x22a000
    IOCTL_VIRTUALAUDIO_WRITE = IOCTL_VIRTUALAUDIO_BASE
    IOCTL_VIRTUALAUDIO_CLEAR_MIC = IOCTL_VIRTUALAUDIO_BASE | (1 << 2)
    IOCTL_VIRTUALAUDIO_GET_MIC_STATUS = IOCTL_VIRTUALAUDIO_BASE | (2 << 2)
    IOCTL_VIRTUALAUDIO_READ = IOCTL_VIRTUALAUDIO_BASE | (10 << 2)

    def __init__(self, device_path=None):
        logger.debug(f"Connecting to virtual audio device at {device_path or self.DEFAULT_DEVICE_PATH}")
        self.device_path = device_path or self.DEFAULT_DEVICE_PATH
        self.handle = win32file.CreateFile(
            self.device_path,
            win32con.GENERIC_WRITE,
            0,
            None,
            win32con.OPEN_EXISTING,
            0,
            None
        )

    def write(self, data):
        """
        Write audio data to the virtual microphone device.
        Data format: 48000Hz, 2 channels, 4 bytes per sample.
        """
        win32file.DeviceIoControl(
            self.handle,
            self.IOCTL_VIRTUALAUDIO_WRITE,
            data,
            None
        )

    def clear_mic(self):
        """Clear the device buffer."""
        win32file.DeviceIoControl(
            self.handle,
            self.IOCTL_VIRTUALAUDIO_CLEAR_MIC,
            None,
            None
        )

    def clear_speaker(self):
        """
        Clear the speaker buffer by reading until no more data is returned.
        """
        pass

    def get_mic_status(self):
        buf = win32file.DeviceIoControl(
            self.handle,
            self.IOCTL_VIRTUALAUDIO_GET_MIC_STATUS,
            None,
            8  # struct: 2 x ULONG (4 bytes each)
        )
        used_size, free_size = struct.unpack("LL", buf)
        return used_size, free_size

    def read(self, size):
        """
        Read audio data from the virtual microphone device.
        format: 48000Hz, 2 channels, 2 bytes per sample.
        """
        buf = win32file.DeviceIoControl(
            self.handle,
            self.IOCTL_VIRTUALAUDIO_READ,
            None,
            size
        )
        return buf

    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
