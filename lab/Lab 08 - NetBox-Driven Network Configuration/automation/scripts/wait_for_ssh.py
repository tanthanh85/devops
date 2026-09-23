#!/usr/bin/env python3
import socket
import sys
import time


if len(sys.argv) != 3:
    raise SystemExit("Usage: wait_for_ssh.py <host> <timeout-seconds>")

host = sys.argv[1]
timeout = int(sys.argv[2])
deadline = time.monotonic() + timeout
last_error = "SSH did not return a protocol banner"

while time.monotonic() < deadline:
    try:
        with socket.create_connection((host, 22), timeout=5) as connection:
            connection.settimeout(10)
            banner = connection.recv(255)
            if banner.startswith(b"SSH-"):
                print(f"SSH protocol banner received from {host}:22")
                raise SystemExit(0)
            last_error = f"unexpected banner: {banner[:80]!r}"
    except OSError as error:
        last_error = str(error)
    time.sleep(10)

raise SystemExit(f"Timed out after {timeout}s waiting for SSH on {host}:22 ({last_error})")
