"""RmdClient: TCP 客户端，发送 SQL 获取响应。"""
from __future__ import annotations

import socket
from .asserts import TestFailure


class RmdbClient:
    def __init__(self, port: int, host: str = "127.0.0.1", timeout: float = 30.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)

    def sql(self, sql: str) -> str:
        payload = sql.encode() + b"\0"
        self.sock.sendall(payload)
        data = bytearray()
        while True:
            chunk = self.sock.recv(8192)
            if not chunk:
                raise TestFailure("server closed connection while waiting for response")
            data.extend(chunk)
            if b"\0" in chunk:
                break
        return data.split(b"\0", 1)[0].decode(errors="replace")

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self) -> "RmdbClient":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
