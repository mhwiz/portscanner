import os
import subprocess
import socket
import threading
import pyfiglet
import psutil
import ipaddress
import time
from queue import Queue

clsc = "cls" if os.name == "nt" else "clear"
subprocess.run(clsc, shell=True, check=True)

banner = pyfiglet.figlet_format("mhwiz \nPython Port Scanner", font= 'doom')

print(banner)

print("Available Network Interface/s", "\n")

addresses = psutil.net_if_addrs()
stats = psutil.net_if_stats()

available_networks = []
for intface, addr_list in addresses.items():
    if any(getattr(addr, 'address').startswith("169.254") for addr in addr_list):
        continue
    elif intface in stats and getattr(stats[intface], "isup"):
        available_networks.append(intface)

ifaceinput = input("Select interface to use: ")
while ifaceinput not in available_networks:
    print("\n","Please select an available interface!", "\n")

    ifaceinput = input("Select interface to use: ")
    print("\n", ifaceinput, "selected", "\n")


def is_valid_ip(ip_str: str) -> bool:
    try:
        ipaddress.ip_address(ip_str.strip())
        return True
    except ValueError:
        return False

target_ip = input("Please enter target: ")
while not is_valid_ip(target_ip):
    print("\nInvalid IP address. Please try again.\n")
    target_ip = input("Please enter target: ")


def parse_ports(port_input: str) -> list[int]:
  
    port_input = port_input.strip()
    ports = set()

    for chunk in port_input.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        if "-" in chunk:
            parts = chunk.split("-")
            if len(parts) != 2:
                raise ValueError(f"Invalid range: '{chunk}'")

            start_str, end_str = parts[0].strip(), parts[1].strip()
            if not (start_str.isdigit() and end_str.isdigit()):
                raise ValueError(f"Invalid range: '{chunk}'")

            start, end = int(start_str), int(end_str)
            if not (1 <= start <= 65535 and 1 <= end <= 65535):
                raise ValueError("Ports must be between 1 and 65535")
            if start > end:
                raise ValueError("Start of range cannot exceed end")

            ports.update(range(start, end + 1))

        else:
            if not chunk.isdigit():
                raise ValueError(f"Invalid port: '{chunk}'")
            port = int(chunk)
            if not (1 <= port <= 65535):
                raise ValueError("Ports must be between 1 and 65535")
            ports.add(port)

    return sorted(ports)

port_input = input("Please enter desired port(s) as single, range (1-1024), or (22,80,443): ")
while True:
    try:
        ports = parse_ports(port_input)
        break
    except ValueError as e:
        print(f"\nInvalid input: {e}\n")
        port_input = input("Please enter desired port(s): ")

print(f"\nScanning {target_ip} on port(s) {len(ports)}...\n")


def port_scan(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((target_ip, port))
        print('port', port, 'open')
    except:
        pass
    finally:
        s.close()

start = time.perf_counter()

q = Queue()
for port in ports:
    q.put(port)


def worker():
    while not q.empty():
        port = q.get()
        port_scan(port)
        q.task_done()

threads = []
for _ in range(min(100, len(ports))):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("\n", f"--- Scan complete in {time.perf_counter() - start:.3f} ms ---\n")
