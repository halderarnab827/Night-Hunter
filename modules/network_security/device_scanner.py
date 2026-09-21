# ============================================================
# NIGHT HUNTER - Target Device Reconnaissance & Scanner
# ============================================================
# Nmap-style targeted device intelligence gathering:
# - Device Name (Reverse DNS / NetBIOS / mDNS)
# - OS Model & Fingerprinting (Windows, Linux, Android, etc.)
# - Device Type (General purpose, phone, router, etc.)
# - MAC Address & Vendor resolution via ARP / Nmap
# - Open TCP Port Scanning
# - Open UDP Port Scanning (Nmap -sU style)
# - Native Python fallback engine when Nmap is not installed
# ============================================================

import os
import re
import socket
import shutil
import platform
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAN_CAUTION = (
    "For local device name, MAC address, and OS model detection, "
    "the target device should be connected to the SAME local network (LAN / Wi-Fi)."
)

TARGET_TCP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 8080, 8443
]

COMMON_UDP_PORTS = {
    53: "DNS",
    67: "DHCP",
    68: "DHCP-CLIENT",
    69: "TFTP",
    123: "NTP",
    135: "MS-RPC",
    137: "NETBIOS-NS",
    138: "NETBIOS-DGM",
    161: "SNMP",
    162: "SNMP-TRAP",
    500: "ISAKMP",
    514: "SYSLOG",
    520: "RIP",
    631: "IPP",
    1434: "MSSQL-M",
    1900: "SSDP",
    4500: "IPSEC-NAT-T",
    5353: "MDNS"
}

OUI_VENDORS = {
    "00:0C:29": "VMware",
    "00:50:56": "VMware",
    "08:00:27": "Oracle VirtualBox",
    "00:15:5D": "Microsoft Hyper-V",
    "98:03:8E": "TP-Link",
    "50:C7:BF": "TP-Link",
    "C0:25:E9": "TP-Link",
    "00:1A:2B": "Cisco",
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "E4:5F:01": "Raspberry Pi",
    "28:CD:C1": "Raspberry Pi",
    "24:0A:C4": "Espressif (ESP32/8266)",
    "30:AE:A4": "Espressif (ESP32/8266)",
    "A4:CF:12": "Espressif (ESP32/8266)",
    "F0:18:98": "Apple",
    "AC:BC:32": "Apple",
    "70:3E:AC": "Apple",
    "88:66:5A": "Apple",
    "BC:D0:74": "Apple",
    "00:1E:67": "Intel",
    "00:21:6A": "Intel",
    "94:E6:F7": "Samsung",
    "40:4E:36": "Samsung",
    "48:2C:A0": "Samsung",
    "00:1A:11": "Google",
    "3C:5A:37": "Google",
    "F4:F5:D8": "Google",
    "58:44:98": "Xiaomi",
    "64:09:80": "Xiaomi",
    "70:89:CC": "Huawei",
    "00:1E:10": "Huawei",
    "00:26:B9": "Dell",
    "00:14:22": "Dell",
    "00:21:CC": "HP",
    "00:1F:29": "HP"
}


def find_nmap_path():
    """Locate Nmap executable on system."""
    paths_to_check = [
        shutil.which("nmap"),
        r"C:\Program Files (x86)\Nmap\nmap.exe",
        r"C:\Program Files\Nmap\nmap.exe",
        "/usr/bin/nmap",
        "/usr/local/bin/nmap",
        "/data/data/com.termux/files/usr/bin/nmap"
    ]
    for p in paths_to_check:
        if p and os.path.exists(p):
            return p
    return None


def get_mac_from_arp(ip):
    """Query system ARP table for MAC address of an IP."""
    try:
        system = platform.system().lower()
        if system == "windows":
            res = subprocess.run(
                ["arp", "-a", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            match = re.search(
                r"([0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2}[:-][0-9a-fA-F]{2})",
                res.stdout
            )
            if match:
                return match.group(1).replace("-", ":").upper()
        else:
            # Linux / Termux / macOS
            arp_cache = "/proc/net/arp"
            if os.path.exists(arp_cache):
                with open(arp_cache, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 4 and parts[0] == ip:
                            mac = parts[3].upper()
                            if mac != "00:00:00:00:00:00":
                                return mac
            res = subprocess.run(
                ["arp", "-n", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            match = re.search(
                r"([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})",
                res.stdout
            )
            if match:
                return match.group(1).upper()
    except Exception:
        pass
    return None


def lookup_mac_vendor(mac):
    """Identify hardware vendor from MAC address prefix."""
    if not mac:
        return ""
    clean_mac = mac.replace("-", ":").upper()
    prefix = clean_mac[:8]
    return OUI_VENDORS.get(prefix, "")


def clean_target_host(target):
    """Normalize input target."""
    if not target:
        return ""
    target = str(target).strip()
    if "://" in target:
        target = target.split("://", 1)[1]
    target = target.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    return target.strip()


def scan_target_nmap(target, scan_udp=True, detect_os=True, timeout=20):
    """
    Execute fast Nmap targeted scan against the target device.
    Extracts device name, OS model, device type, MAC, TCP open ports,
    and UDP open ports (-sU).
    """
    nmap_exe = find_nmap_path()
    if not nmap_exe:
        return None

    tcp_p_str = ",".join(str(p) for p in TARGET_TCP_PORTS)
    udp_p_str = ",".join(str(p) for p in [53, 67, 123, 137, 161, 5353])

    port_arg = f"T:{tcp_p_str},U:{udp_p_str}" if scan_udp else f"T:{tcp_p_str}"

    cmd = [nmap_exe, "-sT"]
    if scan_udp:
        cmd.append("-sU")
    cmd.extend(["-p", port_arg])
    if detect_os:
        cmd.extend(["-O", "--osscan-guess"])
    cmd.extend(["-T4", "-oX", "-", target])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        xml_out = proc.stdout.strip()
        if not xml_out or "<nmaprun" not in xml_out:
            # Fallback if raw sockets or UDP were restricted
            fallback_cmd = [
                nmap_exe, "-sT", "-p", tcp_p_str, "-T4",
                "-oX", "-", target
            ]
            proc = subprocess.run(
                fallback_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            xml_out = proc.stdout.strip()

        if not xml_out or "<nmaprun" not in xml_out:
            return None

        root = ET.fromstring(xml_out)
        host_elem = root.find("host")
        if host_elem is None:
            return None

        # Device Name
        device_name = "Unknown"
        hostname_elem = host_elem.find("hostnames/hostname")
        if hostname_elem is not None:
            device_name = hostname_elem.get("name", "Unknown")

        # IP address & MAC
        ip_address = target
        mac_address = None
        mac_vendor = ""
        for addr in host_elem.findall("address"):
            addr_type = addr.get("addrtype")
            if addr_type == "ipv4":
                ip_address = addr.get("addr", target)
            elif addr_type == "mac":
                mac_address = addr.get("addr")
                mac_vendor = addr.get("vendor", "")

        if not mac_address:
            mac_address = get_mac_from_arp(ip_address)
            if mac_address and not mac_vendor:
                mac_vendor = lookup_mac_vendor(mac_address)

        # OS Model & Device Type
        os_model = "Unknown OS"
        device_type = "general purpose"
        os_elem = host_elem.find("os")
        if os_elem is not None:
            osmatch = os_elem.find("osmatch")
            if osmatch is not None:
                os_name = osmatch.get("name")
                acc = osmatch.get("accuracy")
                os_model = f"{os_name} ({acc}%)" if acc else os_name
                osclass = osmatch.find("osclass")
                if osclass is not None:
                    device_type = osclass.get("type", device_type)

        # Ports
        tcp_ports = []
        udp_ports = []
        for port_elem in host_elem.findall("ports/port"):
            proto = port_elem.get("protocol", "tcp").lower()
            port_id = int(port_elem.get("portid", 0))
            state_elem = port_elem.find("state")
            state = state_elem.get("state", "unknown").upper() if state_elem is not None else "UNKNOWN"
            service_elem = port_elem.find("service")
            service_name = service_elem.get("name", "unknown") if service_elem is not None else "unknown"

            if "OPEN" in state:
                entry = {
                    "port": port_id,
                    "protocol": proto.upper(),
                    "state": state,
                    "service": service_name
                }
                if proto == "tcp":
                    tcp_ports.append(entry)
                elif proto == "udp":
                    udp_ports.append(entry)

        # If device_name is still Unknown, try reverse DNS
        if device_name in ("Unknown", "localhost") and target not in ("127.0.0.1", "localhost"):
            try:
                resolved_name = socket.gethostbyaddr(ip_address)[0]
                if resolved_name:
                    device_name = resolved_name
            except Exception:
                pass

        # If OS is still Unknown OS, try heuristics
        if os_model == "Unknown OS":
            open_pids = {p["port"] for p in tcp_ports}
            if 135 in open_pids or 445 in open_pids or 3389 in open_pids:
                os_model = "Microsoft Windows"
            elif 22 in open_pids:
                os_model = "Linux / Unix (OpenSSH active)"

        return {
            "target": target,
            "ip_address": ip_address,
            "device_name": device_name,
            "os_model": os_model,
            "device_type": device_type,
            "mac_address": mac_address,
            "mac_vendor": mac_vendor,
            "caution": LAN_CAUTION,
            "tcp_ports": tcp_ports,
            "udp_ports": udp_ports,
            "total_open_ports": len(tcp_ports) + len(udp_ports),
            "scan_engine": "Nmap " + (root.get("version") or "Engine"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": True
        }

    except Exception:
        return None


def probe_udp_port(ip, port, timeout=1.2):
    """Send protocol-specific UDP probes to detect open UDP services."""
    probes = {
        53: b"\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07version\x04bind\x00\x00\x10\x00\x03",
        123: b"\x1b" + 47 * b"\0",
        137: b"\x80\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00\x00!\x00\x01",
        1900: b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nMX: 1\r\nST: ssdp:all\r\n\r\n",
        5353: b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09_services\x07_dns-sd\x04_udp\x05local\x00\x00\x0c\x00\x01"
    }
    payload = probes.get(port, b"\x00" * 4)
    service_name = COMMON_UDP_PORTS.get(port, "unknown")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(payload, (ip, port))
        data, _ = sock.recvfrom(1024)
        if data:
            return {"port": port, "protocol": "UDP", "state": "OPEN", "service": service_name}
    except socket.timeout:
        if port in (53, 123, 137, 5353):
            return {"port": port, "protocol": "UDP", "state": "OPEN|FILTERED", "service": service_name}
    except Exception:
        pass
    finally:
        sock.close()
    return None


def probe_tcp_port(ip, port, timeout=1.2):
    """Check TCP port status."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        res = sock.connect_ex((ip, port))
        if res == 0:
            try:
                svc = socket.getservbyport(port, "tcp")
            except Exception:
                svc = "unknown"
            return {"port": port, "protocol": "TCP", "state": "OPEN", "service": svc}
    except Exception:
        pass
    finally:
        sock.close()
    return None


def ping_and_get_ttl(ip):
    """Ping host to check reachability and extract TTL for OS fingerprinting."""
    system = platform.system().lower()
    cmd = ["ping", "-n", "1", "-w", "1500", ip] if system == "windows" else ["ping", "-c", "1", "-W", "2", ip]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            match = re.search(r"TTL=(\d+)", res.stdout, re.IGNORECASE)
            if match:
                return True, int(match.group(1))
            return True, None
    except Exception:
        pass
    return False, None


def scan_target_native(target, scan_udp=True, detect_os=True):
    """
    Native Python scanner for device recon when Nmap is not installed.
    Gathers reverse DNS device name, ping TTL, OS fingerprint, MAC address,
    and scans common TCP and UDP ports.
    """
    clean_target = clean_target_host(target)
    if not clean_target:
        return {
            "target": "",
            "success": False,
            "error": "Target is empty."
        }

    try:
        ip_address = socket.gethostbyname(clean_target)
    except Exception as e:
        return {
            "target": clean_target,
            "success": False,
            "error": f"Cannot resolve host: {e}"
        }

    # Device Name via Reverse DNS
    device_name = "Unknown"
    try:
        host_tuple = socket.gethostbyaddr(ip_address)
        if host_tuple and host_tuple[0]:
            device_name = host_tuple[0]
    except Exception:
        pass

    # Ping & TTL check
    reachable, ttl = ping_and_get_ttl(ip_address)

    # MAC Address & Vendor
    mac_address = get_mac_from_arp(ip_address)
    mac_vendor = lookup_mac_vendor(mac_address) if mac_address else ""

    # TCP Port Scan
    tcp_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(probe_tcp_port, ip_address, p) for p in TARGET_TCP_PORTS]
        for f in as_completed(futures):
            res = f.result()
            if res:
                tcp_ports.append(res)
    tcp_ports.sort(key=lambda x: x["port"])

    # UDP Port Scan
    udp_ports = []
    if scan_udp:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(probe_udp_port, ip_address, p) for p in [53, 67, 123, 137, 161, 5353]]
            for f in as_completed(futures):
                res = f.result()
                if res:
                    udp_ports.append(res)
        udp_ports.sort(key=lambda x: x["port"])

    # OS Model Fingerprinting heuristics
    open_tcp_ids = {p["port"] for p in tcp_ports}
    os_model = "Unknown OS"
    device_type = "general purpose"

    if 135 in open_tcp_ids or 445 in open_tcp_ids or 3389 in open_tcp_ids:
        os_model = "Microsoft Windows (SMB/RDP active)"
    elif 22 in open_tcp_ids:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((ip_address, 22))
            banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
            s.close()
            if "Ubuntu" in banner:
                os_model = "Linux (Ubuntu Server)"
            elif "Debian" in banner:
                os_model = "Linux (Debian)"
            else:
                os_model = "Linux / Unix (OpenSSH active)"
        except Exception:
            os_model = "Linux / Unix"
    elif ttl:
        if 65 <= ttl <= 128:
            os_model = "Microsoft Windows (TTL heuristic)"
        elif 1 <= ttl <= 64:
            os_model = "Linux / Android / macOS (TTL heuristic)"
        elif 129 <= ttl <= 255:
            os_model = "Network Appliance / Cisco (TTL heuristic)"
            device_type = "router / switch"

    return {
        "target": clean_target,
        "ip_address": ip_address,
        "device_name": device_name,
        "os_model": os_model,
        "device_type": device_type,
        "mac_address": mac_address,
        "mac_vendor": mac_vendor,
        "caution": LAN_CAUTION,
        "tcp_ports": tcp_ports,
        "udp_ports": udp_ports,
        "total_open_ports": len(tcp_ports) + len(udp_ports),
        "scan_engine": "Native Python Scanner (Fallback)",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": True
    }


def get_device_recon(target, scan_udp=True, detect_os=True):
    """
    Main entry point for Target Device Reconnaissance.
    Attempts Nmap scan first; automatically falls back to Native Scanner if
    Nmap is unavailable or execution fails.
    """
    clean_target = clean_target_host(target)
    if not clean_target:
        return {
            "target": "",
            "success": False,
            "error": "Target device host or IP is required."
        }

    # 1. Try Nmap if installed
    nmap_result = scan_target_nmap(clean_target, scan_udp=scan_udp, detect_os=detect_os)
    if nmap_result and nmap_result.get("success") and (nmap_result.get("tcp_ports") or nmap_result.get("udp_ports") or nmap_result.get("os_model") != "Unknown OS"):
        return nmap_result

    # 2. Fallback to Native Python Recon
    return scan_target_native(clean_target, scan_udp=scan_udp, detect_os=detect_os)
