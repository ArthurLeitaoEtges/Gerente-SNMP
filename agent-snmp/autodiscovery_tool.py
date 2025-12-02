#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tradução completa do programa C para Python.
Funciona em Linux. Mantém os nomes de ficheiros e formato de saída parecidos com o original.
"""

import os
import sys
import time
import threading
import subprocess
import socket
import struct
import errno
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(BASE_DIR, "config.cfg")
IP_STR_LEN = 64
MAC_STR_LEN = 32
MAX_HOSTS = (1 << 20)

# --- estruturas 'tipo' ---
class Config:
    def __init__(self):
        self.network = "192.168.1.0"
        self.cidr = 24
        self.interval = 60
        self.timeout = 1
        self.start_host = -1
        self.end_host = -1
        self.threads = 10
        self.history_file = os.path.join(BASE_DIR, "discoveries.txt")
        self.changes_file = os.path.join(BASE_DIR, "changes.txt")
        self.last_seen_file = os.path.join(BASE_DIR, "last_seen.txt")

class Device:
    def __init__(self, ip="", mac="", first_seen=None):
        self.ip = ip
        self.mac = mac
        if first_seen is None:
            self.first_seen = "??"
        else:
            self.first_seen = first_seen

# --- OUI table ---
oui_table = []  # list of (prefix, vendor) where prefix like "AA:BB:CC"

# --- utilitários IP / conversão ---
def ip_to_uint(ipstr):
    try:
        packed = socket.inet_aton(ipstr)
        return struct.unpack("!I", packed)[0]
    except Exception:
        raise ValueError("Invalid IPv4 address: {}".format(ipstr))

def uint_to_ip(u):
    return socket.inet_ntoa(struct.pack("!I", u))

def trim(s):
    # remove leading/trailing whitespace and comments after '#'
    s2 = s.split('#', 1)[0].strip()
    return s2

# --- config loader ---
def load_config(path, cfg):
    if not os.path.exists(path):
        print(f"Aviso: não foi possível abrir config '{path}' (usando defaults). errno={errno.ENOENT}")
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = trim(line)
            if not line:
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = trim(key)
            val = trim(val)
            if key == "network":
                cfg.network = val
            elif key == "cidr":
                try:
                    cfg.cidr = int(val)
                except:
                    pass
            elif key == "interval":
                try:
                    cfg.interval = int(val)
                except:
                    pass
            elif key == "timeout":
                try:
                    cfg.timeout = int(val)
                except:
                    pass
            elif key == "start_host":
                try:
                    cfg.start_host = int(val)
                except:
                    pass
            elif key == "end_host":
                try:
                    cfg.end_host = int(val)
                except:
                    pass
            elif key == "threads":
                try:
                    cfg.threads = int(val)
                except:
                    pass
            elif key == "history_file":
                cfg.history_file = os.path.join(BASE_DIR, val)
            elif key == "changes_file":
                cfg.changes_file = os.path.join(BASE_DIR, val)
            elif key == "last_seen_file":
                cfg.last_seen_file = os.path.join(BASE_DIR, val)

# --- calc network range ---
def calc_network_range(cfg):
    if cfg.cidr < 0 or cfg.cidr > 32:
        raise ValueError("CIDR fora do intervalo")
    try:
        net = ip_to_uint(cfg.network)
    except ValueError as e:
        raise
    if cfg.cidr == 32:
        hosts = 1
    else:
        hosts = 1 << (32 - cfg.cidr)
    if hosts == 0 or hosts > MAX_HOSTS:
        raise ValueError("Número de hosts inválido ou maior que limite")
    mask = 0 if cfg.cidr == 0 else (~0 << (32 - cfg.cidr)) & 0xFFFFFFFF
    base = net & mask
    broadcast = (base + hosts - 1) & 0xFFFFFFFF
    if cfg.start_host >= 0 and cfg.end_host >= 0:
        first_host = (base + cfg.start_host) & 0xFFFFFFFF
        last_host = (base + cfg.end_host) & 0xFFFFFFFF
    else:
        if hosts <= 2:
            first_host = base
            last_host = broadcast
        else:
            first_host = base + 1
            last_host = broadcast - 1
    return base, first_host, last_host

# --- quick ping (uses system ping) ---
def ping_ip_quick(ip, timeout):
    # timeout in seconds (integer)
    # return True if host reachable (exit status 0)
    # Use subprocess.run to avoid shell injection
    try:
        # -c 1: one packet, -W timeout: timeout in seconds for reply (Linux ping)
        res = subprocess.run(["ping", "-c", "1", "-W", str(timeout), ip],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0
    except FileNotFoundError:
        # ping not available
        return False
    except Exception:
        return False

# --- read /proc/net/arp to get MAC for IP ---
def get_mac_for_ip(ip):
    try:
        with open("/proc/net/arp", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return "??:??:??:??:??:??"
    # first line is header
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 4:
            ipf = parts[0]
            mac = parts[3]
            if ipf == ip:
                return mac
    return "??:??:??:??:??:??"

# --- OUI loader ---
def load_oui_table(path):
    global oui_table
    if not os.path.exists(path):
        print(f"Aviso: não foi possível abrir {path}")
        return
    cnt = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line or line.startswith('#') or line.strip() == "":
                continue
            parts = line.strip().split(None, 1)
            if len(parts) < 2:
                continue
            hexcode = parts[0].strip()
            vendor_raw = parts[1].strip()
            if len(hexcode) == 6:
                # format prefix as XX:XX:XX
                hexcode = hexcode.upper()
                prefix = "{}:{}:{}".format(hexcode[0:2], hexcode[2:4], hexcode[4:6])
                vendor = vendor_raw
                # strip things like "(hex) vendor" -> keep vendor after ')' if present
                if ')' in vendor:
                    vendor = vendor.split(')', 1)[1]
                vendor = vendor.strip()
                oui_table.append((prefix, vendor))
                cnt += 1
    print(f"Carregado {cnt} prefixos OUI.")

def mac_to_vendor(mac):
    if not mac or len(mac) < 8:
        return "DESCONHECIDO"
    if mac.startswith("??"):
        return "DESCONHECIDO"
    # normalize mac like "aa:bb:cc:dd:ee:ff" or "aa-bb-cc-..."
    m = mac.replace("-", ":").upper()
    parts = m.split(':')
    if len(parts) < 3:
        return "DESCONHECIDO"
    prefix = "{}:{}:{}".format(parts[0], parts[1], parts[2])
    for p, v in oui_table:
        if p == prefix:
            return v
    return "DESCONHECIDO"

# --- is default gateway (reads /proc/net/route) ---
def is_default_gateway(ip):
    try:
        with open("/proc/net/route", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return False
    for line in lines[1:]:
        cols = line.strip().split()
        # expected at least: iface dest gateway flags refcnt use metric mask mtu window irtt
        if len(cols) >= 11:
            iface = cols[0]
            dest_hex = cols[1]
            gw_hex = cols[2]
            try:
                dest = int(dest_hex, 16)
            except:
                continue
            if dest == 0:
                # gateway hex is little-endian in /proc/net/route
                try:
                    gw = int(gw_hex, 16)
                    gw_bytes = struct.pack("<I", gw)
                    gw_ip = socket.inet_ntoa(gw_bytes)
                    return gw_ip == ip
                except Exception:
                    continue
    return False

# --- heuristic TTL (simple wrapper) ---
def heuristic_ttl(ip):
    # original C used ping_host -> heuristic_ttl returned ping_host result; keep same.
    return ping_ip_quick(ip, 1)

# --- is_router heuristic: default gateway OR responds to some well-known ports (80/443/23) ---
def is_router(ip):
    if is_default_gateway(ip):
        return True
    if ping_ip_quick(ip, 1):
        if heuristic_ttl(ip):
            # try connecting to ports (TCP) quickly with timeout
            try_ports = [80, 443, 23]
            for port in try_ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    s.connect((ip, port))
                    s.close()
                    return True
                except Exception:
                    continue
    return False

# --- load last seen file format: "IP MAC FIRST_SEEN" per line ---
def load_last_seen(path):
    if not os.path.exists(path):
        return []
    arr = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = trim(line)
            if not line:
                continue
            parts = line.split(None, 2)
            if len(parts) >= 3:
                ip = parts[0]
                mac = parts[1]
                first_seen = parts[2]
            elif len(parts) == 2:
                ip = parts[0]
                mac = parts[1]
                first_seen = "??"
            else:
                continue
            d = Device(ip=ip, mac=mac, first_seen=first_seen)
            arr.append(d)
    return arr

# --- save device list (last_seen) ---
def save_device_list(path, devices):
    try:
        with open(path, "w", encoding="utf-8") as f:
            for d in devices:
                router = is_router(d.ip)
                vendor = mac_to_vendor(d.mac)
                f.write(f"{d.ip} {d.mac} {vendor} [{ 'ROTEADOR' if router else 'HOST' }] {d.first_seen}\n")
    except Exception as e:
        print("Erro ao salvar last_seen:", e)

# --- append history (append to history_file) ---
def append_history(path, devices):
    try:
        with open(path, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"=== Scan em {now} — {len(devices)} host(s) ativos ===\n")
            for d in devices:
                router = is_router(d.ip)
                vendor = mac_to_vendor(d.mac)
                f.write(f"{d.ip} {d.mac} {vendor} [{'ROTEADOR' if router else 'HOST'}] {d.first_seen}\n")
            f.write("\n")
    except Exception as e:
        print("Erro ao escrever history:", e)

# --- append changes (new/gone) ---
def append_changes(path, newd, gone):
    if len(newd) == 0 and len(gone) == 0:
        return
    try:
        with open(path, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"=== Mudanças em {now} ===\n")
            if len(newd) > 0:
                f.write(f"Novos dispositivos ({len(newd)}):\n")
                for d in newd:
                    router = is_router(d.ip)
                    vendor = mac_to_vendor(d.mac)
                    f.write(f" + {d.ip} {d.mac} {vendor} [{'ROTEADOR' if router else 'HOST'}] {d.first_seen}\n")
            if len(gone) > 0:
                f.write(f"Dispositivos offline ({len(gone)}):\n")
                for d in gone:
                    router = is_router(d.ip)
                    vendor = mac_to_vendor(d.mac)
                    f.write(f" - {d.ip} {d.mac} {vendor} [{'ROTEADOR' if router else 'HOST'}] {d.first_seen}\n")
            f.write("\n")
    except Exception as e:
        print("Erro ao escrever changes:", e)

# --- contains helper ---
def contains(arr, ip):
    for d in arr:
        if d.ip == ip:
            return True
    return False

# --- worker thread ---
class Worker(threading.Thread):
    def __init__(self, thread_id, first_host, last_host, nthreads, timeout, lock_print):
        super().__init__()
        self.thread_id = thread_id
        self.first_host = first_host
        self.last_host = last_host
        self.nthreads = nthreads
        self.timeout = timeout
        self.found = []
        self.lock_print = lock_print

    def run(self):
        # iterate through assigned IPs (step by nthreads)
        ip = self.first_host + self.thread_id
        while ip <= self.last_host:
            ipstr = uint_to_ip(ip)
            with self.lock_print:
                print(f"[Thread {self.thread_id:02d}] Consultando: {ipstr}")
            if ping_ip_quick(ipstr, self.timeout):
                mac = get_mac_for_ip(ipstr)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                d = Device(ip=ipstr, mac=mac, first_seen=now)
                self.found.append(d)
                if is_router(ipstr):
                    with self.lock_print:
                        print(f"[INFO] {ipstr} é o gateway (ROTEADOR)")
            ip += self.nthreads

# --- parallel_scan orchestration ---
def parallel_scan(first_host, last_host, nthreads, timeout):
    threads = []
    lock_print = threading.Lock()
    for i in range(nthreads):
        w = Worker(i, first_host, last_host, nthreads, timeout, lock_print)
        threads.append(w)
        w.start()
    for t in threads:
        t.join()
    all_found = []
    for t in threads:
        all_found.extend(t.found)
    return all_found

# --- main ---
def main(argv):
    cfgpath = argv[1] if len(argv) >= 2 else DEFAULT_CONFIG
    cfg = Config()
    load_config(cfgpath, cfg)

    # load oui table file if present
    load_oui_table(os.path.join(BASE_DIR, "oui.txt"))

    try:
        net_base, first_host, last_host = calc_network_range(cfg)
    except Exception as e:
        print("Erro ao calcular range da rede.", e)
        sys.exit(1)

    total_hosts = last_host - first_host + 1 if last_host >= first_host else 0
    if total_hosts == 0:
        print("Nenhum host no intervalo.")
        sys.exit(1)
    if cfg.threads < 1:
        cfg.threads = 1

    print(f"Config: network={cfg.network}/{cfg.cidr} hosts={total_hosts} interval={cfg.interval} timeout={cfg.timeout} threads={cfg.threads}")
    print(f"history_file={cfg.history_file} changes_file={cfg.changes_file} last_seen_file={cfg.last_seen_file}")

    prev = load_last_seen(cfg.last_seen_file)

    try:
        while True:
            cur = parallel_scan(first_host, last_host, cfg.threads, cfg.timeout)
            append_history(cfg.history_file, cur)

            # find new and gone
            newd = []
            gone = []
            for d in cur:
                if not contains(prev, d.ip):
                    newd.append(d)
            for d in prev:
                if not contains(cur, d.ip):
                    gone.append(d)

            if len(newd) > 0 or len(gone) > 0:
                append_changes(cfg.changes_file, newd, gone)
                print(f"Mudanças detectadas: +{len(newd)} / -{len(gone)}")
            else:
                print("Nenhuma mudança detectada.")

            save_device_list(cfg.last_seen_file, cur)

            prev = cur

            print(f"Próxima varredura em {cfg.interval} segundos...\n")
            sys.stdout.flush()
            time.sleep(cfg.interval)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário. Saindo.")
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
