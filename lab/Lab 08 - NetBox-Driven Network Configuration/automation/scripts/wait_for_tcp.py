#!/usr/bin/env python3
import socket
import sys
import time


host = sys.argv[1]
port = int(sys.argv[2])
timeout = int(sys.argv[3])
deadline = time.monotonic() + timeout

while time.monotonic() < deadline:
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"TCP {host}:{port} is reachable")
            raise SystemExit(0)
    except OSError:
        time.sleep(10)

raise SystemExit(f"Timed out after {timeout}s waiting for TCP {host}:{port}")
