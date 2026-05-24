from pyholomodelink.client import HoloModeLinkClient
from pyholomodelink.commands.system import SystemCommand
from pyholomodelink.commands.video import VideoCommand


class HoloModeLink:
    """Main interface for controlling a HoloModeLink device."""

    def __init__(self, host: str = "192.168.5.1", cmd_port: int = 8077, data_port: int = 8078) -> None:
        client = HoloModeLinkClient(host, cmd_port, data_port)
        self.system = SystemCommand(client)
        self.video = VideoCommand(client)
