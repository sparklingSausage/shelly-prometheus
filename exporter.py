import time
import os
import threading
import requests
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, REGISTRY
from dotenv import load_dotenv

load_dotenv()

SHELLY_HOST = os.getenv("SHELLY_HOST")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))
PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)

power_watts = Gauge("shelly_power_watts", "Current power usage in watts")
relay_state = Gauge("shelly_relay_state", "Relay state (0=off, 1=on)")
energy_total = Gauge("shelly_energy_kwh", "Total energy used in kWh")
voltage = Gauge("shelly_voltage_volts", "Voltage in volts")

def poll_shelly():
    while True:
        try:
            resp = requests.get(f"{SHELLY_HOST}/rpc/Switch.GetStatus?id=0", timeout=5)
            if resp.ok:
                data = resp.json()
                power_watts.set(data["apower"])
                relay_state.set(1 if data["output"] else 0)
                energy_total.set(data["aenergy"]["total"] / 1000)  # Wh to kWh
            voltage_resp = requests.get(f"{SHELLY_HOST}/rpc/Switch.GetConfig?id=0")
            if voltage_resp.ok:
                voltage_data = voltage_resp.json()
                voltage.set(voltage_data.get("voltage", 230))  # fallback to 230V
        except Exception as e:
            print(f"[ERROR] Failed to poll Shelly: {e}")
        time.sleep(POLL_INTERVAL)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

if __name__ == "__main__":
    thread = threading.Thread(target=poll_shelly, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=PORT)
