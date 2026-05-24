from pyholomodelink.client import HoloModeLinkClient
from pyholomodelink.messages import (
    NO_RECV_DATA,
    UNEXPECTED_ERROR,
    DELETE_ALL_ERROR,
    DELETE_FILE_NOT_EXIST_ERROR,
    REBOOT_TIMEOUT_ERROR,
    INVALID_DATE_TIME_ERROR,
    CLOCK_DISPLAY_PARAM_ERROR
)
from pyholomodelink.exceptions import (
    GetBrightnessError,
    SetBrightnessError,
    GetFileListError,
    DeleteAllError,
    DeleteFileError,
    GetVersionError,
    RebootError,
    GetDateTimeError,
    SetDateTimeError,
    GetClockDisplayError,
    SetClockDisplayError
)
from pyholomodelink.const import (
    POOLING_RATE,
    PROC_COMPLETE_WAIT,
    REBOOT_TIMEOUT
)

import re
import time
from datetime import datetime
from collections.abc import Generator
from dataclasses import dataclass

@dataclass
class RebootStatus:
    """Data class for device reboot status."""
    timestamp: str
    status: str
    can_connect: bool

class SystemCommand:
    """Command class for device system settings."""

    def __init__(self, client: HoloModeLinkClient) -> None:
        self._client = client

    def _get_tstamp(self) -> str:
        now = datetime.now()
        ms = now.microsecond // 1000
        return now.strftime(f"%Y-%m-%d %H:%M:%S.{ms:03d}")
    
    def get_bl(self) -> int:
        """Get the screen brightness of the device.

        Returns:
            Brightness value.
        """
        if not (response := self._client.send_cmd("[get_bl]")):
            raise GetBrightnessError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[get_bl\]\[(\d+)\]', response):
            return int(msg.group(1))
        else:
            raise GetBrightnessError(UNEXPECTED_ERROR)

    def set_bl(self, brightness: int) -> int:
        """Set the screen brightness of the device.

        Args:
            brightness: Brightness value to set.

        Returns:
            Brightness value after setting.
        """
        if not (response := self._client.send_cmd(f"[set_bl][{brightness}]")):
            raise SetBrightnessError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[set_bl\]\[(\d+)\]', response):
            return int(msg.group(1))
        else:
            raise SetBrightnessError(UNEXPECTED_ERROR)
        
    def get_file_list(self) -> list[str]:
        """Get a list of files stored on the device.

        Returns:
            List of file names.
        """
        if not (response := self._client.send_cmd("[get_file_list]")):
            raise GetFileListError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[get_file_list\]\[(.+)\]', response):
            return msg.group(1).split(",")
        else:
            raise GetFileListError(UNEXPECTED_ERROR)
    
    def delete_all(self) -> bool:
        """Delete all files stored on the device.

        Returns:
            True if all files were deleted successfully.
        """
        if not (response := self._client.send_cmd(f"[delete_all]")):
            raise DeleteAllError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[delete_all\]\[(.+)\]', response):
            if msg.group(1) == "OK":
                return True
            elif msg.group(1) == "Error":
                raise DeleteAllError(DELETE_ALL_ERROR)
            else:
                raise DeleteAllError(f"{UNEXPECTED_ERROR}({msg.group(1)})")
        else:
            raise DeleteAllError(UNEXPECTED_ERROR)

    def delete_file(self, file_name: str) -> bool:
        """Delete a specific file stored on the device.

        Args:
            file_name: Name of the file to delete.

        Returns:
            True if the file was deleted successfully.
        """
        if not (response := self._client.send_cmd(f"[delete_file][{file_name}]")):
            raise DeleteFileError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[delete_file\]\[(.+)\]', response):
            if msg.group(1) == f"{file_name},OK":
                return True
            elif msg.group(1) == f"{file_name},Not Such File":
                raise DeleteFileError(f"{DELETE_FILE_NOT_EXIST_ERROR}(File: {file_name})")
            else:
                raise DeleteFileError(f"{UNEXPECTED_ERROR}({msg.group(1)})")
        else:
            raise DeleteFileError(UNEXPECTED_ERROR)
            
    def get_version(self) -> str:
        """Get the firmware version of the device.

        Returns:
            Firmware version string.
        """
        if not (response := self._client.send_cmd(f"[get_version]")):
            raise GetVersionError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[get_version\]\[(.+)\]', response):
            return msg.group(1)
        else:
            raise GetVersionError(UNEXPECTED_ERROR)
    
    def reboot(self) -> bool:
        """Send a reboot command to the device.

        Returns:
            True if the reboot command was accepted.
        """
        if not (response := self._client.send_cmd(f"[reboot]")):
            raise RebootError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[reboot\]\[(OK)\]', response):
            return True
        else:
            raise RebootError(UNEXPECTED_ERROR)
            
    def iter_reboot(self, tout: int = REBOOT_TIMEOUT) -> Generator[RebootStatus]:
        """Reboot the device and yield status until it becomes reachable again.

        Yields RebootStatus with status "Running" before rebooting,
        "Rebooting" while waiting, and "Rebooted" when the device responds.

        Args:
            tout: Timeout in seconds to wait for the device to come back online.

        Raises:
            RebootError: If the device does not respond within the timeout.
        """
        timeout = time.monotonic() + tout
        try:
            self.get_bl()
            yield RebootStatus(
                timestamp=self._get_tstamp(),
                status="Running",
                can_connect=True
            )
        except (OSError, GetBrightnessError):
            yield RebootStatus(
                timestamp=self._get_tstamp(),
                status="Not Responding",
                can_connect=False
            )
            return

        self.reboot()
        
        time.sleep(PROC_COMPLETE_WAIT)
        while timeout > time.monotonic():
            try:
                self.get_bl()
                yield RebootStatus(
                    timestamp=self._get_tstamp(),
                    status="Rebooted",
                    can_connect=True
                )
                return
            except (OSError, GetBrightnessError):
                yield RebootStatus(
                    timestamp=self._get_tstamp(),
                    status="Rebooting",
                    can_connect=False
                )
            time.sleep(POOLING_RATE)
        
        raise RebootError(REBOOT_TIMEOUT_ERROR)
    
    def get_datetime(self) -> str:
        """Get the current date and time of the device.

        Returns:
            Date and time string in 'YYYYMMDD-HHMMSS' format.
        """
        if not (response := self._client.send_cmd(f"[get_datetime]")):
            raise GetDateTimeError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[get_datetime\]\[(\d{8}-\d{6})\]', response):
            return msg.group(1)
        else:
            raise GetDateTimeError(UNEXPECTED_ERROR)
        
    def set_datetime(self, dt: str) -> str:
        """Set the date and time of the device.

        Args:
            dt: Date and time string in 'YYYYMMDD-HHMMSS' format.

        Returns:
            Date and time string confirmed by the device.
        """
        if not (response := self._client.send_cmd(f"[set_datetime][{dt}]")):
            raise SetDateTimeError(NO_RECV_DATA)

        if msg := re.search(r'^\[set_datetime\]\[(.+)\]', response):
            if msg.group(1) == dt:
                return dt
            elif msg.group(1) == "Error,Invalid Date":
                raise SetDateTimeError(INVALID_DATE_TIME_ERROR)
            else:
                raise SetDateTimeError(f"{UNEXPECTED_ERROR}({msg.group(1)})")
        else:
            raise SetDateTimeError(UNEXPECTED_ERROR)
        
    def get_clock_display(self) -> dict:
        """Get the clock display settings of the device.

        Returns:
            Dict with keys 'enable', 'color', 'y_offset' retrieved from the device.
        """
        if not (response := self._client.send_cmd(f"[get_clock_display]")):
            raise GetClockDisplayError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[get_clock_display\]\[(\d,\w+,\d+)\]', response):
            msg = msg.group(1).split(',')
            return {"enable":int(msg[0]), "color":msg[1], "y_offset":int(msg[2])}
        else:
            raise GetClockDisplayError(UNEXPECTED_ERROR)
        
    def set_clock_display(self, enable: int, color: str, y_offset: int) -> dict:
        """Set the clock display settings of the device.

        Args:
            enable: 1 to enable the clock display, 0 to disable.
            color: Clock color name (e.g. 'white', 'black').
            y_offset: Vertical position of the clock (1-100).

        Returns:
            Dict with keys 'enable', 'color', 'y_offset' confirmed by the device.
        """
        if not (response := self._client.send_cmd(f"[set_clock_display][{enable},{color},{y_offset}]")):
            raise SetClockDisplayError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[set_clock_display\]\[(.+)\]', response):
            if msg.group(1) == f"{enable},{color},{y_offset}":
                msg = msg.group(1).split(',')
                return {"enable":int(msg[0]), "color":msg[1], "y_offset":int(msg[2])}
            else:
                raise SetClockDisplayError(f"{CLOCK_DISPLAY_PARAM_ERROR}({msg.group(1)})")
        else:
            raise SetClockDisplayError(UNEXPECTED_ERROR)