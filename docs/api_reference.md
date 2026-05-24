# API Reference

## Table of Contents

- [HoloModeLink](#holomodelink)
- [HoloModeLinkClient](#holomodelinkclient)
- [SystemCommand](#systemcommand)
  - [get_bl](#get_bl)
  - [set_bl](#set_bl)
  - [get_file_list](#get_file_list)
  - [delete_all](#delete_all)
  - [delete_file](#delete_file)
  - [get_version](#get_version)
  - [reboot](#reboot)
  - [iter_reboot](#iter_reboot)
  - [get_datetime](#get_datetime)
  - [set_datetime](#set_datetime)
  - [get_clock_display](#get_clock_display)
  - [set_clock_display](#set_clock_display)
- [VideoCommand](#videocommand)
  - [session_begin](#session_begin)
  - [session_end](#session_end)
  - [send_file](#send_file)
  - [iter_watch_recv_status](#iter_watch_recv_status)
  - [apply_video](#apply_video)
- [Data Classes](#data-classes)
  - [RebootStatus](#rebootstatus)
  - [RecvStatus](#recvstatus)
- [Exceptions](#exceptions)
- [Constants](#constants)

---

## HoloModeLink

```python
class HoloModeLink(host: str = "192.168.5.1", cmd_port: int = 8077, data_port: int = 8078)
```

Main interface for controlling a HoloModeLink device. Holds instances of `SystemCommand` and `VideoCommand`.

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `host` | `str` | `"192.168.5.1"` | IP address of the device |
| `cmd_port` | `int` | `8077` | Command port |
| `data_port` | `int` | `8078` | Data transfer port |

### Attributes

| Name | Type | Description |
|------|------|-------------|
| `system` | `SystemCommand` | Access to system commands |
| `video` | `VideoCommand` | Access to video commands |

### Example

```python
from pyholomodelink import HoloModeLink

link = HoloModeLink(host="192.168.5.1")

# With custom ports
link = HoloModeLink(host="192.168.5.1", cmd_port=8077, data_port=8078)
```

---

## HoloModeLinkClient

```python
class HoloModeLinkClient(
    host: str = "192.168.5.1",
    cmd_port: int = 8077,
    data_port: int = 8078
)
```

Low-level TCP socket wrapper. Not intended for direct use — access it through `HoloModeLink` instead.

### Parameters

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `host` | `str` | `"192.168.5.1"` | IP address of the device |
| `cmd_port` | `int` | `8077` | Command port |
| `data_port` | `int` | `8078` | Data transfer port |

### Methods

#### `send_cmd(data: str, tout: int = 2) -> str`

Sends a text command to the command port (8077) and returns the response.

| Parameter | Description |
|-----------|-------------|
| `data` | Command string to send (`\r\n` is appended automatically) |
| `tout` | Timeout in seconds (default: 2) |

**Raises**:
- `TypeError`: if `data` is not a string
- `TimeoutError`: if no response is received

#### `send_data(data: bytes, tout: int = 120) -> None`

Sends binary data to the data port (8078). Used for file transfers.

| Parameter | Description |
|-----------|-------------|
| `data` | Bytes to send |
| `tout` | Timeout in seconds (default: 120) |

**Raises**:
- `TypeError`: if `data` is not bytes

---

## SystemCommand

```python
class SystemCommand(client: HoloModeLinkClient)
```

Command class for device system operations. Access via `HoloModeLink.system`.

---

### `get_bl`

```python
def get_bl() -> int
```

Gets the screen brightness of the device.

**Returns**: Brightness value (int)

**Raises**:
- `GetBrightnessError`: if no response or unexpected response is received

**Example**:

```python
brightness = link.system.get_bl()
print(brightness)  # e.g. 75
```

---

### `set_bl`

```python
def set_bl(brightness: int) -> int
```

Sets the screen brightness of the device.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `brightness` | `int` | Brightness value to set |

**Returns**: Brightness value confirmed by the device (int)

**Raises**:
- `SetBrightnessError`: if no response or unexpected response is received

**Example**:

```python
confirmed = link.system.set_bl(50)
print(confirmed)  # 50
```

---

### `get_file_list`

```python
def get_file_list() -> list[str]
```

Gets a list of files stored on the device.

**Returns**: List of file names

**Raises**:
- `GetFileListError`: if no response or unexpected response is received

**Example**:

```python
files = link.system.get_file_list()
print(files)  # ["video1.mp4"]
```

---

### `delete_all`

```python
def delete_all() -> bool
```

Deletes all files stored on the device.

**Returns**: `True` on success

**Raises**:
- `DeleteAllError`: if deletion fails, no response, or unexpected response is received

**Example**:

```python
link.system.delete_all()
```

---

### `delete_file`

```python
def delete_file(file_name: str) -> bool
```

Deletes a specific file stored on the device.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `file_name` | `str` | Name of the file to delete |

**Returns**: `True` on success

**Raises**:
- `DeleteFileError`: if the file does not exist (message: `"File does not exist on device."`), deletion fails, or no response is received

**Example**:

```python
link.system.delete_file("video1.mp4")
```

---

### `get_version`

```python
def get_version() -> str
```

Gets the firmware version of the device.

**Returns**: Version string (e.g. `"1.2.3"`)

**Raises**:
- `GetVersionError`: if no response or unexpected response is received

**Example**:

```python
version = link.system.get_version()
print(version)  # "1.2.3"
```

---

### `reboot`

```python
def reboot() -> bool
```

Sends a reboot command to the device. Only confirms that the command was accepted — does not wait for the reboot to complete.  
Use [`iter_reboot`](#iter_reboot) if you need to wait until the device is back online.

**Returns**: `True` if the command was accepted

**Raises**:
- `RebootError`: if no response or unexpected response is received

**Example**:

```python
link.system.reboot()
```

---

### `iter_reboot`

```python
def iter_reboot(tout: int = 60) -> Generator[RebootStatus]
```

Sends a reboot command and yields [`RebootStatus`](#rebootstatus) until the device becomes reachable again.

Polling interval is `POOLING_RATE` (0.5 s). After sending the reboot command, an initial wait of `PROC_COMPLETE_WAIT` (4.0 s) is applied before polling begins.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `tout` | `int` | `60` | Timeout in seconds to wait for the device to come back online |

**Yields**: [`RebootStatus`](#rebootstatus)

Status transitions:

| `status` | `can_connect` | When |
|----------|--------------|------|
| `"Running"` | `True` | Before reboot (device is responding) |
| `"Not Responding"` | `False` | Device is not reachable before reboot (returns immediately) |
| `"Rebooting"` | `False` | Device is rebooting (not yet responding) |
| `"Rebooted"` | `True` | Reboot complete (device is responding again) |

**Raises**:
- `RebootError`: if the device does not respond within the timeout

**Example**:

```python
for status in link.system.iter_reboot(tout=60):
    print(f"[{status.timestamp}] {status.status} (reachable: {status.can_connect})")

# Example output:
# [2024-06-01 12:00:00.000] Running (reachable: True)
# [2024-06-01 12:00:04.500] Rebooting (reachable: False)
# [2024-06-01 12:00:05.000] Rebooting (reachable: False)
# [2024-06-01 12:00:10.200] Rebooted (reachable: True)
```

---

### `get_datetime`

```python
def get_datetime() -> str
```

Gets the current date and time of the device.

**Returns**: Date and time string in `"YYYYMMDD-HHMMSS"` format (e.g. `"20240601-120000"`)

**Raises**:
- `GetDateTimeError`: if no response or unexpected response is received

**Example**:

```python
dt = link.system.get_datetime()
print(dt)  # "20240601-120000"
```

---

### `set_datetime`

```python
def set_datetime(dt: str) -> str
```

Sets the date and time of the device.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `dt` | `str` | Date and time string in `"YYYYMMDD-HHMMSS"` format |

**Returns**: Date and time string confirmed by the device (`"YYYYMMDD-HHMMSS"` format)

**Raises**:
- `SetDateTimeError`: if the format is invalid, no response, or unexpected response is received

**Example**:

```python
result = link.system.set_datetime("20240601-120000")
print(result)  # "20240601-120000"
```

**Sync to current time**:

```python
from datetime import datetime

now = datetime.now().strftime("%Y%m%d-%H%M%S")
link.system.set_datetime(now)
```

---

### `get_clock_display`

```python
def get_clock_display() -> dict
```

Gets the clock display settings of the device.

**Returns**: Dictionary with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `enable` | `int` | Clock display enabled (`1`) or disabled (`0`) |
| `color` | `str` | Clock color name (e.g. `"white"`, `"black"`) |
| `y_offset` | `int` | Vertical position of the clock |

**Raises**:
- `GetClockDisplayError`: if no response or unexpected response is received

**Example**:

```python
clock = link.system.get_clock_display()
print(clock)  # {"enable": 1, "color": "white", "y_offset": 10}
```

---

### `set_clock_display`

```python
def set_clock_display(enable: int, color: str, y_offset: int) -> dict
```

Sets the clock display settings of the device.

**Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `enable` | `int` | `1` to enable the clock display, `0` to disable |
| `color` | `str` | Clock color name (e.g. `"white"`, `"black"`) |
| `y_offset` | `int` | Vertical position of the clock (1–100) |

**Returns**: Dictionary of confirmed settings (same format as `get_clock_display`)

**Raises**:
- `SetClockDisplayError`: if parameters are invalid, no response, or unexpected response is received

**Example**:

```python
result = link.system.set_clock_display(enable=1, color="white", y_offset=10)
print(result)  # {"enable": 1, "color": "white", "y_offset": 10}
```

---

## VideoCommand

```python
class VideoCommand(client: HoloModeLinkClient)
```

Command class for video file transfer operations. Access via `HoloModeLink.video`.

---

### `session_begin`

```python
def session_begin(send_file_num: int = 1) -> bool
```

Begins a file transfer session. Must be called before sending any files.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `send_file_num` | `int` | `1` | Number of files to be sent in this session |

**Returns**: `True` on success

**Raises**:
- `SessionBeginError`: if the session fails to start, no response, or unexpected response is received

---

### `session_end`

```python
def session_end() -> bool
```

Ends the current file transfer session.

If a timeout occurs, a warning is emitted and `True` is returned (the device is assumed to have ended the session).

**Returns**: `True` on success

**Raises**:
- `SessionEndError`: if the session fails to end or an unexpected response is received
- `SendFileError`: if the device reports a file receive error

---

### `send_file`

```python
def send_file(send_file_path: str, wait: float = 4.0) -> None
```

Sends a file to the device. First notifies the device of the file name and size, then transfers the binary data.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `send_file_path` | `str` | — | Path to the file to send |
| `wait` | `float` | `4.0` | Seconds to wait after notifying the device before sending binary data |

**Raises**:
- `TrySendFileError`: if the pre-send notification fails (e.g. not enough space, file creation failed)

**Error cases**:

| Device response | Exception message |
|-----------------|-------------------|
| `"Error,No Enough Space"` | `"Not enough space on device."` |
| `"Error,File Create Failed"` | `"Failed to create file on device."` |
| `"Error"` | `"Failed to send file."` |

---

### `iter_watch_recv_status`

```python
def iter_watch_recv_status(
    file_name: str,
    file_size_bytes: int,
    tout: int = 60
) -> Generator[RecvStatus]
```

Polls the file receive status and yields [`RecvStatus`](#recvstatus) until the file is fully received or a timeout occurs.

Polling interval is `POOLING_RATE` (0.5 s).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file_name` | `str` | — | Name of the file being received |
| `file_size_bytes` | `int` | — | Total size of the file in bytes |
| `tout` | `int` | `60` | Timeout in seconds |

**Yields**: [`RecvStatus`](#recvstatus)

**Raises**:
- `RecvStatusError`: if the file is not fully received within the timeout

**Example**:

```python
import os

file_path = "/path/to/video.mp4"
file_size = os.path.getsize(file_path)

for status in link.video.iter_watch_recv_status("video.mp4", file_size):
    pct = status.recv_file_size / status.file_size * 100
    print(f"[{status.timestamp}] {pct:.1f}% ({status.recv_file_size}/{status.file_size} bytes)")
    if status.received:
        print("Received.")
```

---

### `apply_video`

```python
def apply_video(
    file_path: str,
    wait_time_after_send_file: float = 4.0,
    file_recv_timeout: float = 60
) -> RecvStatus
```

Uploads a video file to the device and waits until it is fully received.  
Handles the full session lifecycle: `session_end` → `session_begin` → `send_file` → poll until received → `session_end`.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `file_path` | `str` | — | Path to the video file to upload |
| `wait_time_after_send_file` | `float` | `4.0` | Seconds to wait after notifying the device before sending binary data |
| `file_recv_timeout` | `float` | `60` | Timeout in seconds to wait for the device to finish receiving |

**Returns**: [`RecvStatus`](#recvstatus) from the final polling iteration

**Raises**:
- `SessionBeginError`, `SessionEndError`, `TrySendFileError`, `RecvStatusError`: if any phase fails

**Flow**:

```
session_end()               # Clear any existing session
  ↓
session_begin()             # Start a new session
  ↓
send_file()                 # Notify device, wait, then send binary data
  ↓
iter_watch_recv_status()    # Poll until fully received
  ↓
session_end()               # End the session
```

**Example**:

```python
result = link.video.apply_video("/path/to/video.mp4")

if result.received:
    print(f"Upload complete: {result.file_name}")
    print(f"Received: {result.recv_file_size} bytes")
```

---

## Data Classes

### RebootStatus

```python
@dataclass
class RebootStatus:
    timestamp: str
    status: str
    can_connect: bool
```

Data class representing device reboot state, yielded by [`iter_reboot`](#iter_reboot).

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `str` | Time the status was recorded (`"YYYY-MM-DD HH:MM:SS.mmm"` format) |
| `status` | `str` | Current state (see table below) |
| `can_connect` | `bool` | Whether the device is reachable |

**`status` values**:

| Value | Meaning |
|-------|---------|
| `"Running"` | Before reboot (device is operating normally) |
| `"Not Responding"` | Device was unreachable before the reboot command was sent |
| `"Rebooting"` | Device is rebooting (not yet responding) |
| `"Rebooted"` | Reboot complete (device is responding) |

---

### RecvStatus

```python
@dataclass
class RecvStatus:
    timestamp: str
    file_name: str
    file_size: int
    recv_file_size: int
    received: bool
```

Data class representing file receive state, yielded by [`iter_watch_recv_status`](#iter_watch_recv_status) and returned by [`apply_video`](#apply_video).

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `str` | Time the status was recorded (`"YYYY-MM-DD HH:MM:SS.mmm"` format) |
| `file_name` | `str` | Name of the file being received |
| `file_size` | `int` | Total file size in bytes |
| `recv_file_size` | `int` | Number of bytes received by the device so far |
| `received` | `bool` | `True` when `recv_file_size >= file_size` |

---

## Exceptions

All exceptions inherit from `HoloModeLinkError`.

```
HoloModeLinkError
├── GetBrightnessError      # Failed to get brightness
├── SetBrightnessError      # Failed to set brightness
├── GetFileListError        # Failed to get file list
├── RecvStatusError         # Failed to check receive status (includes timeout)
├── SessionBeginError       # Failed to start session
├── SessionEndError         # Failed to end session
├── DeleteAllError          # Failed to delete all files
├── DeleteFileError         # Failed to delete a file
├── TrySendFileError        # Failed to notify device before sending file
├── SendFileError           # File send failed (device-side receive error)
├── GetVersionError         # Failed to get firmware version
├── RebootError             # Reboot failed or timed out
├── GetDateTimeError        # Failed to get datetime
├── SetDateTimeError        # Failed to set datetime
├── GetClockDisplayError    # Failed to get clock display settings
└── SetClockDisplayError    # Failed to set clock display settings
```

**Example**:

```python
from pyholomodelink.exceptions import DeleteFileError, HoloModeLinkError

try:
    link.system.delete_file("nonexistent.mp4")
except DeleteFileError as e:
    print(f"Delete error: {e}")
except HoloModeLinkError as e:
    print(f"Unexpected error: {e}")
```

---

## Constants

Internal constants defined in `pyholomodelink.const`.

| Constant | Value | Description |
|----------|-------|-------------|
| `POOLING_RATE` | `0.5` | Polling interval in seconds |
| `PROC_COMPLETE_WAIT` | `4.0` | Default wait time after a command before proceeding (seconds) |
| `FILE_RECV_TIMEOUT` | `60` | Default timeout for file receive operations (seconds) |
| `REBOOT_TIMEOUT` | `60` | Default timeout for reboot operations (seconds) |

---

## Testing

### Unit tests

```bash
PYTHONPATH=src python3 -m pytest tests/commands/ -v
```

### Integration tests (requires a real device)

```bash
PYTHONPATH=src HOLOMODELINK_HOST=<device-ip> python3 -m pytest tests/integration/ -v --timeout=60
```

To include video transfer tests, specify a video file:

```bash
PYTHONPATH=src HOLOMODELINK_HOST=<device-ip> HOLOMODELINK_TEST_VIDEO=/path/to/video.mp4 \
    python3 -m pytest tests/integration/ -v --timeout=60
```

**Environment variables**:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOLOMODELINK_HOST` | `"localhost"` | IP address of the target device |
| `HOLOMODELINK_TEST_VIDEO` | *(unset)* | Path to the video file used in integration tests |
