import os
import time
import threading
import requests
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from dotenv import load_dotenv

load_dotenv()

HOSTS = os.getenv("SHELLY_HOSTS", "").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))
PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)
REGISTRY = CollectorRegistry()

power_watts = Gauge("shelly_power_watts", "Power usage in watts", ["host"], registry=REGISTRY)
relay_state = Gauge("shelly_relay_state", "Relay state (0=off, 1=on)", ["host"], registry=REGISTRY)
energy_total = Gauge("shelly_energy_kwh", "Total energy in kWh", ["host"], registry=REGISTRY)
voltage = Gauge("shelly_voltage_volts", "Voltage in volts", ["host"], registry=REGISTRY)

def poll_shelly(host):
    host_label = host.replace("http://", "").replace("https://", "").strip()

    while True:
        try:
            print(f"[INFO] Polling {host_label}")
            status_url = f"http://{host_label}/rpc/Switch.GetStatus?id=0"
            config_url = f"http://{host_label}/rpc/Switch.GetConfig?id=0"

            resp = requests.get(status_url, timeout=5)
            if resp.ok:
                data = resp.json()
                power_watts.labels(host=host_label).set(data["apower"])
                relay_state.labels(host=host_label).set(1 if data["output"] else 0)
                energy_total.labels(host=host_label).set(data["aenergy"]["total"] / 1000)
            else:
                print(f"[WARN] Failed status response from {host_label}: {resp.status_code}")

            resp2 = requests.get(config_url, timeout=5)
            if resp2.ok:
                v_data = resp2.json()
                voltage.labels(host=host_label).set(v_data.get("voltage", 230))
            else:
                print(f"[WARN] Failed config response from {host_label}: {resp2.status_code}")

        except Exception as e:
            print(f"[ERROR] Polling {host_label} failed: {e}")

        time.sleep(POLL_INTERVAL)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    if not HOSTS or HOSTS == [""]:
        print("[FATAL] No SHELLY_HOSTS defined. Exiting.")
        exit(1)

    for host in HOSTS:
        clean_host = host.strip()
        if clean_host:
            threading.Thread(target=poll_shelly, args=(clean_host,), daemon=True).start()

    print(f"[INFO] Exporter listening on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
