import socket
import urllib.request
import json
import time
import subprocess
import platform

# =====================================
# LANGUAGE SYSTEM
# =====================================

LANG = "PL"

TEXT = {
    "PL": {
        "dns_error": "❌ Błąd DNS",
        "ip": "📡 IP",
        "https_ok": "🟢 HTTPS działa",
        "https_fail": "🔴 HTTPS nie działa",
        "http_fail": "🔴 HTTP nie działa",
        "status": "===== STATUS =====",
        "online": "🟢 ONLINE",
        "partial": "🟡 CZĘŚCIOWO",
        "offline": "🔴 OFFLINE",
        "unknown": "❌ Nieznana komenda",
        "lang_set": "🌐 Język ustawiony na"
    },
    "EN": {
        "dns_error": "❌ DNS error",
        "ip": "📡 IP",
        "https_ok": "🟢 HTTPS OK",
        "https_fail": "🔴 HTTPS FAIL",
        "http_fail": "🔴 HTTP FAIL",
        "status": "===== STATUS =====",
        "online": "🟢 ONLINE",
        "partial": "🟡 PARTIAL",
        "offline": "🔴 OFFLINE",
        "unknown": "❌ Unknown command",
        "lang_set": "🌐 Language set to"
    }
}

def t(k):
    return TEXT[LANG][k]

# =====================================
# PARSERS
# =====================================

def parse_time(t):

    t = t.lower()

    if t.endswith("s"):
        return int(t[:-1])

    if t.endswith("m"):
        return int(t[:-1]) * 60

    if t.endswith("h"):
        return int(t[:-1]) * 3600

    return int(t)

def parse_size(s):

    s = s.lower()

    if s.endswith("b"):
        return int(s[:-1])

    return int(s)

def parse_pps(p):

    p = p.lower()

    if p.endswith("pps"):
        return int(p[:-3])

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

        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

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
# PINGT
# =====================================

def pingt(ip, duration=None, size=32, pps=1):

    print("\n📡 PINGT:", ip)
    print("📦 Packet Size:", size, "B")
    print("⚡ PPS:", pps)

    sent = 0
    recv = 0
    values = []

    start = time.time()

    if pps < 1:
        pps = 1

    delay = 1 / pps

    try:

        while True:

            if duration and time.time() - start >= duration:
                break

            sent += 1

            ok, ms = ping_once(ip, size)

            if ok:
                recv += 1
                values.append(ms)
                print("🟢", round(ms,1), "ms")
            else:
                print("🔴 timeout")

            time.sleep(delay)

    except KeyboardInterrupt:
        pass

    avg = sum(values)/len(values) if values else 0
    loss = ((sent-recv)/sent)*100 if sent else 0

    print("\n===== RAPORT =====")
    print("📦 Loss:", round(loss,1), "%")
    print("📡 Avg:", round(avg,1), "ms")
    print("📨 Packet Size:", size, "B")
    print("📊 Sent:", sent)
    print("📥 Received:", recv)

# =====================================
# WATCHDOG
# =====================================

def watchdog(ip):

    print("\n🛡 WATCHDOG:", ip)

    last = 0
    spikes = 0

    try:

        while True:

            ok, ms = ping_once(ip)

            if ok:

                print("🟢", ms, "ms")

                if last and abs(ms-last) > 80:
                    spikes += 1
                    print("⚠️ SPIKE")

                last = ms

            else:
                print("🔴 LOST")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⚠️ SPIKES:", spikes)

# =====================================
# NETHEALTH
# =====================================

def nethealth(ip):

    print("\n🧠 NETHEALTH:", ip)

    vals = []
    loss = 0

    for i in range(10):

        ok, ms = ping_once(ip)

        if ok:
            vals.append(ms)
            print("🟢", ms, "ms")
        else:
            loss += 1
            print("🔴 loss")

        time.sleep(0.5)

    avg = sum(vals)/len(vals) if vals else 999

    print("\n===== RESULT =====")
    print("📡 Avg:", round(avg,1))
    print("📦 Loss:", loss)

# =====================================
# GAMETEST
# =====================================

def gametest(ip):

    print("\n🎮 GAMETEST:", ip)

    vals = []
    jitter = []
    loss = 0
    last = None

    for i in range(15):

        ok, ms = ping_once(ip)

        if ok:

            vals.append(ms)
            print("🟢", ms, "ms")

            if last:
                jitter.append(abs(ms-last))

            last = ms

        else:
            loss += 1
            print("🔴 loss")

        time.sleep(0.4)

    avg = sum(vals)/len(vals) if vals else 999
    jit = sum(jitter)/len(jitter) if jitter else 0

    print("\n===== GAMING =====")
    print("📡 Ping:", round(avg,1))
    print("📊 Jitter:", round(jit,1))
    print("📦 Loss:", loss)

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
            urllib.request.urlopen(
                "http://ip-api.com/json/" + ip,
                timeout=3
            ).read().decode()
        )

        if data.get("status") != "success":
            print("❌ FAIL")
            return

        print("📡 IP:", data["query"])
        print("🌍 Country:", data["country"])
        print("🏙 City:", data["city"])
        print("📶 ISP:", data["isp"])
        print("🧭 Region:", data["regionName"])
        print("🏢 Org:", data["org"])

    except Exception as e:
        print("❌ ERROR:", e)

# =====================================
# WEBSCAN
# =====================================

def webscan(domain):

    print("\n🌐 WEBSCAN:", domain)

    try:
        ip = socket.gethostbyname(domain)
        print(t("ip") + ":", ip)
    except:
        print(t("dns_error"))
        return

    https_ok = False
    http_ok = False

    print("\n🔐 HTTPS:")

    try:
        urllib.request.urlopen("https://" + domain, timeout=3)
        https_ok = True
        print(t("https_ok"))
    except:
        print(t("https_fail"))

    print("\n🌍 HTTP:")

    try:
        urllib.request.urlopen("http://" + domain, timeout=3)
        http_ok = True
        print("🟢 HTTP OK")
    except:
        print(t("http_fail"))

    print("\n" + t("status"))

    if https_ok:
        print(t("online"))
    elif http_ok:
        print(t("partial"))
    else:
        print(t("offline"))

# =====================================
# MYIP
# =====================================

def myip():

    print("\n🧾 MY IP")

    try:
        local = socket.gethostbyname(socket.gethostname())
        print("🏠 Local IP:", local)
    except:
        print("🏠 Local IP: ERROR")

    try:

        data = json.loads(
            urllib.request.urlopen(
                "https://api.ipify.org?format=json",
                timeout=3
            ).read().decode()
        )

        print("🌍 Public IP:", data["ip"])

    except:
        print("🌍 Public IP: ERROR")

# =====================================
# LANGUAGE
# =====================================

def language(lang):

    global LANG

    if lang.upper() in ["PL", "POLSKI"]:
        LANG = "PL"
        print(t("lang_set"), "PL")

    elif lang.upper() in ["EN", "ENGLISH"]:
        LANG = "EN"
        print(t("lang_set"), "EN")

    else:
        print("PL / EN only")

# =====================================
# HELP MENU
# =====================================

def help_menu():

    print("""

===== ULTI TOOL v1.2 =====

.pingt <ip> [time] [size] [pps]
.watchdog <ip>
.nethealth <ip>
.gametest <ip>

.dns <domain>
.geoip <ip>
.webscan <domain>
.myip

.language <PL/EN>

.help
.exit

Examples:
.pingt 8.8.8.8
.pingt 8.8.8.8 10s
.pingt 8.8.8.8 10s 128b
.pingt 8.8.8.8 10s 128b 5pps

============================
""")

# =====================================
# MAIN LOOP
# =====================================

help_menu()

while True:

    cmd = input("ULTI> ").strip()

    if cmd == ".help":
        help_menu()

    elif cmd.startswith(".pingt "):

        parts = cmd.split()

        ip = parts[1]

        duration = None
        size = 32
        pps = 1

        for part in parts[2:]:

            # PPS FIRST (important fix)
            if part.endswith("pps"):
                pps = parse_pps(part)

            elif part.endswith("b"):
                size = parse_size(part)

            elif part.endswith(("s", "m", "h")):
                duration = parse_time(part)

        pingt(ip, duration, size, pps)

    elif cmd.startswith(".watchdog "):
        watchdog(cmd.split()[1])

    elif cmd.startswith(".nethealth "):
        nethealth(cmd.split()[1])

    elif cmd.startswith(".gametest "):
        gametest(cmd.split()[1])

    elif cmd.startswith(".dns "):
        dns(cmd.split()[1])

    elif cmd.startswith(".geoip "):
        geoip(cmd.split()[1])

    elif cmd.startswith(".webscan "):
        webscan(cmd.split()[1])

    elif cmd == ".myip":
        myip()

    elif cmd.startswith(".language "):
        language(cmd.split()[1])

    elif cmd == ".exit":
        break

    else:
        print(t("unknown"))
