class HoloModeLinkError(Exception):
    """Base exception for HoloModeLink errors."""

class GetBrightnessError(HoloModeLinkError):
    """Raised when the brightness cannot be retrieved."""

class SetBrightnessError(HoloModeLinkError):
    """Raised when the brightness cannot be set."""

class GetFileListError(HoloModeLinkError):
    """Raised when the file list cannot be retrieved."""

class RecvStatusError(HoloModeLinkError):
    """Raised when the receive status cannot be checked."""
    
class SessionBeginError(HoloModeLinkError):
    """Raised when a session cannot be started."""

class SessionEndError(HoloModeLinkError):
    """Raised when a session cannot be ended."""

class DeleteAllError(HoloModeLinkError):
    """Raised when all files cannot be deleted."""

class DeleteFileError(HoloModeLinkError):
    """Raised when a file cannot be deleted."""

class TrySendFileError(HoloModeLinkError):
    """Raised when a file cannot be sent."""

class SendFileError(HoloModeLinkError):
    """Raised when a file cannot be sent."""

class GetVersionError(HoloModeLinkError):
    """Raised when the device version cannot be retrieved."""

class RebootError(HoloModeLinkError):
    """Raised when the device cannot be rebooted."""

class GetDateTimeError(HoloModeLinkError):
    """Raised when the device date and time cannot be retrieved."""

class SetDateTimeError(HoloModeLinkError):
    """Raised when the device date and time cannot be set."""

class GetClockDisplayError(HoloModeLinkError):
    """Raised when the clock display cannot be retrieved."""

class SetClockDisplayError(HoloModeLinkError):
    """Raised when the clock display cannot be set."""