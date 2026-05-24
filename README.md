# pyholomodelink

Python library for controlling a [HoloModeLink](https://holomodels.jp/holomodelink) device over TCP.

## What is HoloModeLink?

[HoloModeLink](https://holomodels.jp/holomodelink) is a compact digital display designed for viewing your favorite digital figures, avatars, and video content in your room on a daily basis.

## Requirements

- Python 3.9+

## Installation

```bash
pip install -e .
```

## Usage

```python
from pyholomodelink import HoloModeLink

link = HoloModeLink(host="192.168.5.1")
```

### System

```python
# Brightness
link.system.get_bl()
link.system.set_bl(50)

# Firmware version
link.system.get_version()

# File list
link.system.get_file_list()
link.system.delete_file("video.mp4")
link.system.delete_all()

# Date and time
link.system.get_datetime()          # "YYYYMMDD-HHMMSS"
link.system.set_datetime("20240601-120000")

# Clock display
link.system.get_clock_display()     # {"enable": 1, "color": "white", "y_offset": 10}
link.system.set_clock_display(enable=1, color="white", y_offset=10)

# Reboot
for status in link.system.iter_reboot():
    print(status.timestamp, status.status, status.can_connect)
```

### Video

```python
# Upload a video file
result = link.video.apply_video("/path/to/video.mp4")
print(result.received, result.file_name, result.recv_file_size)

# Session control
link.video.session_begin()
link.video.session_end()
```

## Connection

| Port | Purpose |
|------|---------|
| 8077 | Command (TCP) |
| 8078 | Data / file transfer (TCP) |

## Notice

This library is an unofficial Python wrapper for the HoloModeLink device API.
The implementation is based solely on the publicly available official API specification:
[HoloModeLink Official API Reference](https://drive.google.com/file/d/1rG2Ece8ZX-rAl_VGwDvPwlg24d7UbvDu/view)

All rights to the HoloModeLink device and its API belong to the respective manufacturer.
This project is not affiliated with or endorsed by the manufacturer.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Running Tests

### Unit tests

```bash
PYTHONPATH=src python3 -m pytest tests/commands/ -v
```

### Integration tests (requires a real device)

```bash
PYTHONPATH=src HOLOMODELINK_HOST=<device-ip> python3 -m pytest tests/integration/ -v --timeout=60
```

To run video transfer tests, specify a video file:

```bash
PYTHONPATH=src HOLOMODELINK_HOST=<device-ip> HOLOMODELINK_TEST_VIDEO=/path/to/video.mp4 \
    python3 -m pytest tests/integration/ -v --timeout=60
```
