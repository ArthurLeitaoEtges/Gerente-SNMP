import asyncio
import os
import time
from datetime import datetime
import snmp_agent
from snmp_agent import VariableBinding, OctetString, Integer, Gauge32, Counter32, TimeTicks, IPAddress, utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LAST_SEEN_FILE = os.path.join(BASE_DIR, "last_seen.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "discoveries.txt")
CONFIG_FILE = os.path.join(BASE_DIR, "config.cfg")

# MIB base: experimental 1.3.6.1.3.2025
MIB_BASE = "1.3.6.1.3.2025"

OID_DISCOVERY_RUNS = MIB_BASE + ".1.1"       # discoveryRuns (Counter32)
OID_DEVICES_FOUND = MIB_BASE + ".1.2"       # devicesFound (Gauge32)
OID_LAST_DISCOVERY = MIB_BASE + ".1.3"      # lastDiscoveryTime (TimeTicks)

OID_CONFIG_SCAN_INTERVAL = MIB_BASE + ".3.1"  # scanInterval (Integer) read-write in MIB
OID_CONFIG_LOG_LEVEL = MIB_BASE + ".3.2"      # logLevel (Integer)

# Raiz da tabela discoveryTable: .2.1 -> as entradas ficam em .2.1.1.<coluna>.<índice>
# Registro esses valores usando os OIDs completos.
# deviceIndex     -> .2.1.1.1.<index>
# deviceIp        -> .2.1.1.2.<index>
# deviceName      -> .2.1.1.3.<index>
# deviceMac       -> .2.1.1.4.<index>
# responseTime    -> .2.1.1.5.<index>
# lastSeen        -> .2.1.1.6.<index>
TABLE_ROOT_PREFIX = MIB_BASE + ".2.1.1"

def read_config_values():
    """Lê escalares do config.cfg (scanInterval e logLevel). Se não existir, usa defaults."""
    scan_interval = 60
    log_level = 2
    if not os.path.exists(CONFIG_FILE):
        return scan_interval, log_level
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.split('#',1)[0].strip()
                if not line or '=' not in line:
                    continue
                k, v = [x.strip() for x in line.split('=',1)]
                if k == "interval":
                    try:
                        scan_interval = int(v)
                    except:
                        pass
                elif k == "logLevel":
                    try:
                        log_level = int(v)
                    except:
                        pass
    except Exception:
        pass
    return scan_interval, log_level

def load_last_seen_devices():
    devices = []
    if not os.path.exists(LAST_SEEN_FILE):
        return devices
    try:
        with open(LAST_SEEN_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(None, 4)

                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]

                    if len(parts) >= 5:
                        first_seen = parts[4]
                    elif len(parts) == 4:
                        first_seen = parts[3]
                    else:
                        first_seen = "??"

                    devices.append({
                        "ip": ip,
                        "mac": mac,
                        "name": "-",
                        "responseTime": 0,
                        "firstSeen": first_seen
                    })
    except Exception:
        pass
    return devices

def count_history_runs():
    """Conta quantas varreduras existem no HISTORY_FILE procurando cabeçalhos '=== Scan em' (compatível com autodiscovery_tool.py)."""
    if not os.path.exists(HISTORY_FILE):
        return 0
    cnt = 0
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("=== Scan em"):
                    cnt += 1
    except Exception:
        pass
    return cnt

def last_discovery_timeticks():
    """
    Retorna TimeTicks (centésimos de segundo) desde a última modificação do HISTORY_FILE.
    Se HISTORY_FILE não existir, retorna 0.
    """
    if not os.path.exists(HISTORY_FILE):
        return 0
    try:
        mtime = os.path.getmtime(HISTORY_FILE)
        now = time.time()
        delta_sec = max(0.0, now - mtime)

        ticks = int(delta_sec * 100)
        return ticks
    except Exception:
        return 0

async def handler(req: snmp_agent.SNMPRequest) -> snmp_agent.SNMPResponse:

    scan_interval, log_level = read_config_values()
    devices = load_last_seen_devices()
    runs = count_history_runs()
    last_disc_ticks = last_discovery_timeticks()
    devices_count = len(devices)

    vbs = []

    vbs.append(VariableBinding(OID_DISCOVERY_RUNS + ".0", Counter32(runs)))
    vbs.append(VariableBinding(OID_DEVICES_FOUND + ".0", Gauge32(devices_count)))
    vbs.append(VariableBinding(OID_LAST_DISCOVERY + ".0", TimeTicks(last_disc_ticks)))

    vbs.append(VariableBinding(OID_CONFIG_SCAN_INTERVAL + ".0", Integer(scan_interval)))
    vbs.append(VariableBinding(OID_CONFIG_LOG_LEVEL + ".0", Integer(log_level)))

    # tabela: montar entradas completas (colunas x index)
    # col 1 -> deviceIndex (Integer)
    # col 2 -> deviceIp (IpAddress)
    # col 3 -> deviceName (OctetString)
    # col 4 -> deviceMac (OctetString)
    # col 5 -> responseTime (TimeTicks)
    # col 6 -> lastSeen (TimeTicks)
    for idx, d in enumerate(devices, start=1):
        base_idx = f"{TABLE_ROOT_PREFIX}"

        vbs.append(VariableBinding(f"{base_idx}.1.{idx}", Integer(idx)))

        vbs.append(VariableBinding(f"{base_idx}.2.{idx}", OctetString(d.get("ip","-"))))
        vbs.append(VariableBinding(f"{base_idx}.3.{idx}", OctetString(d.get("name","-"))))
        vbs.append(VariableBinding(f"{base_idx}.4.{idx}", OctetString(d.get("mac","-"))))
        vbs.append(VariableBinding(f"{base_idx}.5.{idx}", TimeTicks(d.get("responseTime",0))))

        try:

            t = d.get("firstSeen", "??")
            if t and t != "??":
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                delta = now - dt
                ticks = int(delta.total_seconds() * 100)
            else:
                ticks = 0
        except Exception:
            ticks = 0
        vbs.append(VariableBinding(f"{base_idx}.6.{idx}", TimeTicks(ticks)))


    res_vbs = utils.handle_request(req=req, vbs=vbs)
    res = req.create_response(res_vbs)
    return res

async def main():

    host = "0.0.0.0"
    port = 16100
    server = snmp_agent.Server(handler=handler, host=host, port=port)
    print(f"SNMP agent listening on {host}:{port} (MIB base {MIB_BASE})")
    await server.start()
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
