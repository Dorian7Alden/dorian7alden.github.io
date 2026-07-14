"""Server: 管理 rmdb server 进程生命周期。"""
from __future__ import annotations

import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path
from typing import Optional

from .asserts import BAD_LOG_RE, TestFailure
from .client import RmdbClient


class Server:
    def __init__(self, repo: Path, port: int, log_dir: Path, name: str):
        self.repo = repo
        self.build = repo / "build"
        self.port = port
        self.name = name
        self.db = f"tk_{name}_{int(time.time() * 1000)}"
        self.log = log_dir / f"{name}.server.log"
        self.proc: Optional[subprocess.Popen] = None

    @property
    def binary(self) -> Path:
        return self.build / "bin" / "rmdb"

    def start(self, clean: bool = True) -> None:
        if clean:
            shutil.rmtree(self.build / self.db, ignore_errors=True)
        self._kill_existing_port_owner()
        with self.log.open("wb") as out:
            self.proc = subprocess.Popen(
                [str(self.binary), self.db],
                cwd=str(self.build),
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise TestFailure(f"server exited early; log={self.log}")
            try:
                s = socket.create_connection(("127.0.0.1", self.port), timeout=0.2)
                s.close()
                return
            except OSError:
                time.sleep(0.1)
        raise TestFailure(f"server did not accept connections; log={self.log}")

    def client(self) -> RmdbClient:
        return RmdbClient(self.port)

    def stop(self, kill: bool = False) -> None:
        if self.proc is None:
            return
        if self.proc.poll() is None:
            if kill:
                self.proc.kill()
            else:
                try:
                    os.killpg(self.proc.pid, signal.SIGINT)
                except ProcessLookupError:
                    pass
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self.proc = None

    def restart_same_db(self) -> None:
        self.stop(kill=True)
        with self.log.open("ab") as out:
            out.write(b"\n--- restart same db ---\n")
        with self.log.open("ab") as out:
            self.proc = subprocess.Popen(
                [str(self.binary), self.db],
                cwd=str(self.build),
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise TestFailure(f"server exited early after restart; log={self.log}")
            try:
                s = socket.create_connection(("127.0.0.1", self.port), timeout=0.2)
                s.close()
                return
            except OSError:
                time.sleep(0.1)
        raise TestFailure(f"server did not restart; log={self.log}")

    def cleanup_db(self) -> None:
        shutil.rmtree(self.build / self.db, ignore_errors=True)

    def assert_log_clean(self) -> None:
        if self.log.exists():
            text = self.log.read_text(errors="replace")
            m = BAD_LOG_RE.search(text)
            if m:
                raise TestFailure(f"server log contains {m.group(0)!r}; log={self.log}")

    def _kill_existing_port_owner(self) -> None:
        subprocess.run(
            ["pkill", "-9", "-x", "rmdb"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.2)
