import socket
import urllib.request
import json
import time
import subprocess
import platform
import re

# =====================================
# ULTI TOOL v1.4 FINAL
# =====================================

LANG = "PL"

TEXT = {
    "PL": {
        "dns_error": "❌ Błąd DNS",
        "ip": "📡 IP",
        "unknown": "❌ Nieznana komenda",
        "no_net": "❌ BRAK POŁĄCZENIA"
    }
}

def t(k):
    return TEXT[LANG][k]

# =====================================
# PARSERS
# =====================================

def parse_time(ti):
    ti = ti.lower()
    if ti.endswith("s"): return int(ti[:-1])
    if ti.endswith("m"): return int(ti[:-1]) * 60
    if ti.endswith("h"): return int(ti[:-1]) * 3600
    return int(ti)

def parse_size(s):
    s = s.lower()
    if s.endswith("b"): return int(s[:-1])
    return int(s)

def parse_pps(p):
    p = p.lower()
    if p.endswith("pps"): return int(p[:-3])
    return int(p)

# =====================================
# PING CORE
# =====================================

def ping_once(ip, size=32):
    try:
        system = platform.system().lower()

        if system == "windows":
            cmd = f"ping -n 1 -l {size} {ip}"
        else:
            cmd = f"ping -c 1 -s {size} {ip}"

        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        out = r.stdout.lower()

        if "time=" in out:
            line = out.split("time=")[1]
            ms = line.split("ms")[0]
            ms = ms.replace("<", "").replace("=", "").strip()
            return True, float(ms)

        return False, None

    except:
        return False, None

# =====================================
# PINGT (FULL FIXED)
# =====================================

def pingt(ip, duration=None, size=32, pps=1):

    print("\n📡 PINGT START")
    print("--------------------")
    print(f"🎯 IP: {ip}")
    print(f"📦 SIZE: {size} B")
    print(f"⚡ PPS: {pps}")
    print(f"⏱ TIME: {duration if duration else '∞'}")
    print("--------------------\n")

    sent = 0
    recv = 0
    times = []

    start = time.time()
    delay = 1 / max(pps, 1)

    try:
        while True:

            if duration and time.time() - start >= duration:
                break

            sent += 1

            ok, ms = ping_once(ip, size)

            if ok:
                recv += 1
                times.append(ms)
                print(f"🟢 {ip} | {ms:.1f} ms")
            else:
                print(f"🔴 {ip} | timeout")

            time.sleep(delay)

    except KeyboardInterrupt:
        pass

    avg = sum(times)/len(times) if times else 0
    loss = ((sent - recv) / sent) * 100 if sent else 0
    total_bytes = sent * size

    print("\n===== PING STATS =====")
    print(f"📡 IP: {ip}")
    print(f"📨 Sent: {sent}")
    print(f"📥 Received: {recv}")
    print(f"📦 Loss packets: {sent - recv}")
    print(f"📉 Loss %: {round(loss,1)}%")
    print(f"⏱ Avg ping: {round(avg,1)} ms")
    print(f"💾 Bytes sent: {total_bytes} B ({round(total_bytes/1024,2)} KB)")
    print("======================\n")

# =====================================
# DNS
# =====================================

def dns(domain):
    print("\n🌐 DNS:", domain)

    try:
        ip = socket.gethostbyname(domain)
        print(t("ip") + ":", ip)
    except:
        print(t("dns_error"))

# =====================================
# GEOIP
# =====================================

def geoip(ip):

    print("\n🌍 GEOIP:", ip)

    try:
        data = json.loads(
            urllib.request.urlopen("http://ip-api.com/json/" + ip, timeout=3)
            .read().decode()
        )

        if data["status"] != "success":
            print("❌ FAIL")
            return

        print("📡 IP:", data["query"])
        print("🌍 Country:", data["country"])
        print("🏙 City:", data["city"])
        print("📶 ISP:", data["isp"])
        print("🏢 Org:", data["org"])

    except:
        print("❌ ERROR")

# =====================================
# WEBSCAN
# =====================================

def webscan(domain):

    print("\n🌐 WEBSCAN:", domain)

    try:
        ip = socket.gethostbyname(domain)
        print("📡 IP:", ip)
    except:
        print(t("dns_error"))
        return

    try:
        urllib.request.urlopen("https://" + domain, timeout=3)
        print("🟢 HTTPS OK")
    except:
        print("🔴 HTTPS FAIL")

    try:
        urllib.request.urlopen("http://" + domain, timeout=3)
        print("🟢 HTTP OK")
    except:
        print("🔴 HTTP FAIL")

# =====================================
# MY IP
# =====================================

def myip():

    print("\n🧾 MY IP")

    try:
        local = socket.gethostbyname(socket.gethostname())
        print("🏠 Local:", local)
    except:
        print("ERROR")

    try:
        data = json.loads(
            urllib.request.urlopen("https://api.ipify.org?format=json", timeout=3)
            .read().decode()
        )
        print("🌍 Public:", data["ip"])
    except:
        print("ERROR")

# =====================================
# CONVERT
# =====================================

def convert(value_unit, target_unit):

    units = {
        "b": 1,
        "kb": 1e3,
        "mb": 1e6,
        "gb": 1e9,
        "tb": 1e12
    }

    match = re.match(r"([0-9.]+)([a-z]+)", value_unit.lower())

    if not match:
        print("❌ .convert 5gb b")
        return

    value = float(match.group(1))
    unit = match.group(2)

    if unit not in units or target_unit not in units:
        print("❌ jednostka")
        return

    result = value * units[unit] / units[target_unit]

    print(f"📦 {value}{unit.upper()} = {round(result,4)}{target_unit.upper()}")

# =====================================
# NETHERNET
# =====================================

def nethernet():

    print("\n🌐 NETHERNET")

    wifi_ip = None
    eth_ip = None

    system = platform.system().lower()

    if system == "windows":

        out = subprocess.getoutput("ipconfig")

        for b in out.split("\n\n"):

            name = b.split(":")[0].lower()

            ip = re.search(r"IPv4 Address.*?: ([\d\.]+)", b)

            if not ip:
                continue

            ip = ip.group(1)

            if "wi-fi" in name or "wireless" in name:
                wifi_ip = ip

            elif "ethernet" in name:
                eth_ip = ip

    else:
        try:
            wifi_ip = socket.gethostbyname(socket.gethostname())
        except:
            pass

    print("📶 WI-FI:", wifi_ip if wifi_ip else "❌")
    print("🔌 Ethernet:", eth_ip if eth_ip else "❌")

    if not wifi_ip and not eth_ip:
        print(t("no_net"))

# =====================================
# HELP
# =====================================

def help_menu():

    print("""
===== ULTI TOOL v1.4 =====

.pingt <ip> [time] [size] [pps]
.dns <domain>
.geoip <ip>
.webscan <domain>
.myip
.nethernet
.convert 5gb b

.exit
============================
""")

# =====================================
# MAIN LOOP
# =====================================

help_menu()

while True:

    cmd = input("ULTI> ").strip()

    if cmd == ".exit":
        break

    elif cmd.startswith(".pingt "):
        parts = cmd.split()

        ip = parts[1]
        duration = None
        size = 32
        pps = 1

        for part in parts[2:]:

            if part.endswith("pps"):
                pps = parse_pps(part)

            elif part.endswith("b"):
                size = parse_size(part)

            elif part.endswith(("s","m","h")):
                duration = parse_time(part)

        pingt(ip, duration, size, pps)

    elif cmd.startswith(".dns "):
        dns(cmd.split()[1])

    elif cmd.startswith(".geoip "):
        geoip(cmd.split()[1])

    elif cmd.startswith(".webscan "):
        webscan(cmd.split()[1])

    elif cmd == ".myip":
        myip()

    elif cmd == ".nethernet":
        nethernet()

    elif cmd.startswith(".convert "):
        parts = cmd.split()
        convert(parts[1], parts[2])

    else:
        print(t("unknown"))
