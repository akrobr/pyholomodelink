# pyholomodelink Documentation

A Python library for controlling a HoloModeLink device over TCP.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Communication Protocol](#communication-protocol)
- [API Reference](api_reference.md)

---

## Overview

`pyholomodelink` is an unofficial Python library for controlling a HoloModeLink device.  
All communication with the device is done over TCP sockets, using two separate ports — one for commands and one for file transfer.

The library provides two command groups:

| Group | Attribute | Description |
|-------|-----------|-------------|
| System | `HoloModeLink.system` | System-level operations: brightness, datetime, clock display, file management, reboot |
| Video | `HoloModeLink.video` | Video file upload and session management |

> **Notice**: This library is an unofficial wrapper implemented based on the publicly available official API specification.  
> All rights to the HoloModeLink device and its API belong to the respective manufacturer.  
> This project is not affiliated with or endorsed by the manufacturer.

---

## Requirements

- Python 3.9+
- No external dependencies (standard library only)

---

## Installation

Clone the repository and install locally.

```bash
git clone <repository-url>
cd pyholomodelink
pip install -e .
```

---

## Quick Start

### Connecting to the Device

```python
from pyholomodelink import HoloModeLink

# Default IP: 192.168.5.1
link = HoloModeLink()

# Specify an IP address
link = HoloModeLink(host="192.168.5.1")

# Specify custom ports
link = HoloModeLink(host="192.168.5.1", cmd_port=8077, data_port=8078)
```

### System Operations

```python
# Get / set brightness (0–100)
brightness = link.system.get_bl()   # e.g. 75
link.system.set_bl(50)

# Get firmware version
version = link.system.get_version()  # e.g. "1.2.3"

# List files on the device
files = link.system.get_file_list()  # e.g. ["video1.mp4", "video2.mp4"]

# Delete files
link.system.delete_file("video1.mp4")
link.system.delete_all()

# Get / set datetime (format: YYYYMMDD-HHMMSS)
dt = link.system.get_datetime()         # e.g. "20240601-120000"
link.system.set_datetime("20240601-120000")

# Get / set clock display
clock = link.system.get_clock_display()
# {"enable": 1, "color": "white", "y_offset": 10}
link.system.set_clock_display(enable=1, color="white", y_offset=10)

# Reboot and wait until the device is back online
for status in link.system.iter_reboot():
    print(f"[{status.timestamp}] {status.status} (reachable: {status.can_connect})")
```

### Video Upload

```python
# Upload in one call
result = link.video.apply_video("/path/to/video.mp4")

if result.received:
    print(f"Received: {result.file_name} ({result.recv_file_size} bytes)")
```

---

## Communication Protocol

Two TCP ports are used to communicate with the device.

| Port | Purpose | Timeout |
|------|---------|---------|
| 8077 | Command send/receive (text) | 2 s (default) |
| 8078 | Binary data transfer (file upload) | 120 s (default) |

Commands are sent as strings in `[command_name][param]` format, terminated with `\r\n`.  
Responses follow the same format.

```
Send:    [get_bl]\r\n
Receive: [get_bl][75]
```

---

For full API details, see the [API Reference](api_reference.md).
