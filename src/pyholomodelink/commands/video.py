from pyholomodelink.client import HoloModeLinkClient
from pyholomodelink.commands.system import SystemCommand
from pyholomodelink.messages import (
    SESSION_END_TIMEOUT_WARNING,
    NO_RECV_DATA,
    UNEXPECTED_ERROR,
    SESSION_BEGIN_ERROR,
    SESSION_END_ERROR,
    FILE_SEND_ERROR,
    FILE_RECV_ERROR,
    NO_SPACE_ERROR,
    FILE_CREATE_ERROR,
    TIMEOUT_ERROR
)
from pyholomodelink.exceptions import (
    SessionBeginError,
    SessionEndError,
    SendFileError,
    RecvStatusError,
    TrySendFileError
)
from pyholomodelink.const import (
    POOLING_RATE,
    PROC_COMPLETE_WAIT,
    FILE_RECV_TIMEOUT
)

import re
import os
import time
from collections.abc import Generator
from dataclasses import dataclass

@dataclass
class RecvStatus:
    """Data class for file receive status."""
    timestamp: str
    file_name: str
    file_size: int
    recv_file_size: int
    received: bool

class VideoCommand:
    """Command class for video file operations."""

    def __init__(self, client: HoloModeLinkClient) -> None:
        self._client = client
        self.sys_cmd = SystemCommand(client)

    def session_begin(self, send_file_num: int = 1) -> bool:
        """Begin a file transfer session.

        Args:
            send_file_num: Number of files to be sent in this session.

        Returns:
            True if the session started successfully.
        """
        if not (response := self._client.send_cmd(f"[session_begin][{send_file_num}]")):
            raise SessionBeginError(NO_RECV_DATA)
        
        if msg := re.search(r'^\[session_begin\]\[(\w+)\]', response):
            if msg.group(1) == "OK":
                return True
            elif msg.group(1) == "Error":
                raise SessionBeginError(SESSION_BEGIN_ERROR)
            else:
                raise SessionBeginError(f"{UNEXPECTED_ERROR}({msg.group(1)})")
        else:
            raise SessionBeginError(UNEXPECTED_ERROR)
            
    def _prepare_send(self, send_file_path: str) -> bool:
        """Notify the device of the file name and size before sending.

        Args:
            send_file_path: Path to the file to be sent.

        Returns:
            True if the device is ready to receive the file.
        """
        file_name = os.path.basename(send_file_path)
        file_size_bytes = os.path.getsize(send_file_path)

        if not (response := self._client.send_cmd(f"[send_file][{file_name},{file_size_bytes}]")):
            raise TrySendFileError(NO_RECV_DATA)

        if msg := re.search(r'^\[send_file\]\[(.+)\]', response):
            if msg.group(1) == "OK":
                return True
            elif msg.group(1) == "Error":
                raise TrySendFileError(FILE_SEND_ERROR)
            elif msg.group(1) == "Error,No Enough Space":
                raise TrySendFileError(NO_SPACE_ERROR)
            elif msg.group(1) == "Error,File Create Failed":
                raise TrySendFileError(FILE_CREATE_ERROR)
            else:
                raise TrySendFileError(UNEXPECTED_ERROR)
        else:
            raise TrySendFileError(UNEXPECTED_ERROR)
            
    def send_file(self, send_file_path: str, wait: float = PROC_COMPLETE_WAIT) -> None:
        """Send a file to the device over the data port.

        Args:
            send_file_path: Path to the file to send.
            wait: Seconds to wait after notifying the device before sending binary data.
        """
        self._prepare_send(send_file_path)
        time.sleep(wait)
        with open(send_file_path, "rb") as fo:
            self._client.send_data(fo.read())
        
    def session_end(self) -> bool:
        """End the current file transfer session.

        Returns:
            True if the session ended successfully.
        """
        try:
            response = self._client.send_cmd(f"[session_end]")
        except TimeoutError:
            warnings.warn(SESSION_END_TIMEOUT_WARNING)
            return True # If no response is received, assume the session has ended successfully.

        if msg := re.search(r'^\[session_end\]\[(.+)\]', response):
            if msg.group(1) == "OK":
                return True
            elif msg.group(1) == "Error":
                raise SessionEndError(SESSION_END_ERROR)
            else:
                raise SessionEndError(f"{UNEXPECTED_ERROR}({msg.group(1)})")
        elif msg := re.search(r'^\[send_file\]\[(.+)\]', response):
            raise SendFileError(f"{FILE_RECV_ERROR}({msg.group(1)})")
        else:
            raise SessionEndError(UNEXPECTED_ERROR)

    def iter_watch_recv_status(self, file_name: str, file_size_bytes: int, tout: int = FILE_RECV_TIMEOUT) -> Generator[RecvStatus]:
        """Iterate over the file receive status until the file is fully received or a timeout occurs.
        
        Args:
            file_name: Name of the file being received.
            file_size_bytes: Total size of the file being received, in bytes.
            tout: Timeout duration in seconds.

        Yields:
            RecvStatus objects with the current receive status.
        """
        current_file_size = 0
        timeout = time.monotonic() + tout
        while timeout > time.monotonic():
            try:
                if file_list := self.sys_cmd.get_file_list():
                    file_name, current_file_size = file_list[0], int(file_list[1])
            except IndexError:
                file_name, current_file_size = "", 0

            yield RecvStatus(
                timestamp=self.sys_cmd._get_tstamp(),
                file_name=file_name,
                file_size=file_size_bytes,
                recv_file_size=current_file_size,
                received=file_size_bytes <= current_file_size
            )

            if file_size_bytes <= current_file_size:
                return

            time.sleep(POOLING_RATE)

        raise RecvStatusError(TIMEOUT_ERROR)
    
    def apply_video(
            self,
            file_path: str,
            wait_time_after_send_file: float = PROC_COMPLETE_WAIT,
            file_recv_timeout: float = FILE_RECV_TIMEOUT
    ) -> RecvStatus:
        """Upload a video file to the device and wait until it is fully received.

        Args:
            file_path: Path to the video file to upload.
            wait_time_after_send_file: Seconds to wait after sending.
            file_recv_timeout: Timeout in seconds to wait for the device to finish receiving.

        Returns:
            RecvStatus of the final polling result.
        """
        self.session_end()

        self.session_begin()

        self.send_file(file_path, wait_time_after_send_file)

        # Check if the file was received successfully by the device.
        *_, last_recv_status = self.iter_watch_recv_status(
            file_name=os.path.basename(file_path),
            file_size_bytes=os.path.getsize(file_path),
            tout=file_recv_timeout
        )
        self.session_end()
        
        return last_recv_status