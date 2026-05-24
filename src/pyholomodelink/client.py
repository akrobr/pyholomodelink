from pyholomodelink.messages import (
    NO_RECV_DATA
)

import socket

class HoloModeLinkClient:
    def __init__(self, host: str = "192.168.5.1", cmd_port: int = 8077, data_port: int = 8078) -> None:
        self.host = host
        self.cmd_port = cmd_port
        self.data_port = data_port

    def send_cmd(self, data: str, tout: int = 2) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(tout)
            sock.connect((self.host, self.cmd_port))
            if isinstance(data, str):
                sock.sendall((data+"\r\n").encode(encoding="utf-8"))
            else:
                raise TypeError("Data must be a string.")
            
            try:
                return sock.recv(1024).decode(encoding="utf-8")
            except TimeoutError:
                raise TimeoutError(NO_RECV_DATA)
            
    def send_data(self, data: bytes, tout: int = 120) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(tout)
            sock.connect((self.host, self.data_port))
            if isinstance(data, bytes):
                return sock.sendall(data)
            else:
                raise TypeError("Data must be bytes.")
