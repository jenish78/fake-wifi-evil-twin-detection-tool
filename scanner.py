import subprocess
import geocoder
from collections import defaultdict
import joblib
import re
import pandas as pd

# Firewall
from firewall import disconnect_wifi, block_network

# Load ML model
model = joblib.load("model.pkl")

# Prevent repeated blocking
blocked_ssids = set()


def get_location():
    g = geocoder.ip('me')
    return g.latlng if g.latlng else [22.3, 70.8]


def scan_networks(TEST_MODE=False):
    output = subprocess.check_output(
        "netsh wlan show networks mode=bssid",
        shell=True
    ).decode(errors="ignore")

    networks = defaultdict(list)

    ssid = None
    bssid = None
    signal = None
    channel = None
    encryption = None

    # -------- PARSING --------
    for line in output.split("\n"):
        line = line.strip()

        if line.startswith("SSID") and "BSSID" not in line:
            ssid = line.split(":", 1)[1].strip()

        elif line.startswith("BSSID"):
            bssid = line.split(":", 1)[1].strip()

        elif line.startswith("Signal"):
            raw_signal = line.split(":", 1)[1].strip()
            match = re.search(r"\d+", raw_signal)
            signal = int(match.group()) if match else 0

        elif line.startswith("Channel"):
            raw_channel = line.split(":", 1)[1].strip()
            match = re.search(r"\d+", raw_channel)
            channel = int(match.group()) if match else 0

        elif line.startswith("Authentication"):
            encryption = line.split(":", 1)[1].strip()

            if ssid and bssid:
                networks[ssid].append((bssid, signal, encryption, channel))

                # reset
                bssid = None
                signal = None
                channel = None
                encryption = None

    lat, lon = get_location()

    # -------- TEST MODE --------
    if TEST_MODE:
        networks["Fake_Evil_Twin"] = [
            ("AA:BB:CC:DD:EE:01", 80, "WPA2", 6),
            ("AA:BB:CC:DD:EE:02", 60, "WPA2", 11),
            ("AA:BB:CC:DD:EE:03", 50, "WPA2", 1)
        ]

    result = []

    # -------- DETECTION --------
    for ssid, entries in networks.items():

        # ✅ REMOVE DUPLICATES
        unique_entries = {}
        for e in entries:
            bssid = e[0]

            if bssid not in unique_entries or e[1] > unique_entries[bssid][1]:
                unique_entries[bssid] = e

        entries = list(unique_entries.values())

        # Extract data
        bssid_list = [e[0] for e in entries]
        signals = [e[1] for e in entries]
        channels = [e[3] for e in entries]

        unique_bssids = set(bssid_list)
        unique_channels = set(channels)

        bssid_count = len(unique_bssids)

        seen = set()

        for entry in entries:
            bssid, signal, encryption, channel = entry

            key = (ssid, bssid)
            if key in seen:
                continue
            seen.add(key)

            enc_val = 1 if "WPA" in encryption else 0

            # ---------- RULE BASED ----------
            suspicious = False
            reasons = []

            # Rule 1
            if bssid_count >= 3:
                suspicious = True
                reasons.append("Multiple APs")

            # Rule 2
            if signals and (max(signals) - min(signals) > 45):
                suspicious = True
                reasons.append("Signal variation")

            # Rule 3
            if len(unique_channels) >= 3:
                suspicious = True
                reasons.append("Channel variation")

            # ---------- ML SUPPORT ----------
            input_data = pd.DataFrame([{
                "signal": signal if signal else 0,
                "channel": channel if channel else 0,
                "encryption": enc_val,
                "bssid_count": bssid_count
            }])

            prediction = model.predict(input_data)[0]

            if prediction == 1 and suspicious:
                reasons.append("ML confirmed")

            # ---------- FINAL DECISION ----------
            status = "Safe"   # ✅ FIXED ERROR

            if suspicious:
                status = "⚠️ Suspicious"

                # 🔐 FIREWALL (REAL MODE)
                if ssid not in blocked_ssids:
                    print(f"[FIREWALL] Blocking {ssid}")
                    disconnect_wifi()
                    block_network(ssid)
                    blocked_ssids.add(ssid)

            # ---------- CONFIDENCE ----------
            confidence = 80 if not suspicious else min(60 + 10 * len(reasons), 100)

            result.append({
                "ssid": ssid,
                "bssid": bssid,
                "signal": signal,
                "status": status,
                "confidence": f"{confidence}%",
                "reason": ", ".join(reasons) if reasons else "Normal",
                "lat": lat,
                "lon": lon
            })

    return result