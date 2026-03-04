#!/usr/bin/env python3
import socket
import sys
import threading


def forward(source: socket.socket, destination: socket.socket) -> None:
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    except OSError:
        pass
    finally:
        source.close()
        destination.close()


REQUIRED_ARGS = 3


def main() -> None:
    if len(sys.argv) < REQUIRED_ARGS:
        sys.stderr.write("Usage: tailscale_forward.py <tailscale-ip> <port>\n")
        sys.exit(1)

    tailscale_ip = sys.argv[1]
    port = int(sys.argv[2])

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((tailscale_ip, port))
    server.listen(5)
    sys.stdout.write(f"Forwarding {tailscale_ip}:{port} -> 127.0.0.1:{port}\n")
    sys.stdout.flush()

    while True:
        client, _ = server.accept()
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect(("127.0.0.1", port))
        threading.Thread(target=forward, args=(client, target), daemon=True).start()
        threading.Thread(target=forward, args=(target, client), daemon=True).start()


if __name__ == "__main__":
    main()
