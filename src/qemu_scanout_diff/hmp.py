from __future__ import annotations

import socket
import time
from pathlib import Path


def _read_until_prompt(connection: socket.socket, deadline: float) -> bytes:
    data = bytearray()
    while time.monotonic() < deadline:
        try:
            chunk = connection.recv(4096)
        except TimeoutError:
            continue
        if not chunk:
            break
        data.extend(chunk)
        if b"(qemu) " in data:
            break
    return bytes(data)


def run_hmp_command(command: str, host: str = "127.0.0.1", port: int = 4444, timeout: float = 3.0) -> str:
    deadline = time.monotonic() + timeout
    with socket.create_connection((host, port), timeout=timeout) as connection:
        connection.settimeout(0.2)
        _read_until_prompt(connection, deadline)
        connection.sendall(command.rstrip("\n").encode("ascii") + b"\n")
        response = _read_until_prompt(connection, deadline)
    return response.decode("latin1", errors="replace")


def capture_scanout(output_path: str | Path, address: int, size: int, host: str = "127.0.0.1", port: int = 4444, timeout: float = 3.0) -> str:
    output = str(Path(output_path))
    return run_hmp_command(f"pmemsave 0x{address:X} {size} {output}", host, port, timeout)
