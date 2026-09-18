import time
import random
import requests
import argparse
from datetime import datetime, timezone

URL = "http://127.0.0.1:8000/api/telemetry"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--scenario",
    choices=["normal", "high_temp", "low_temp", "rapid_rise", "cooling_failure"],
    default="normal"
)

args = parser.parse_args()
scenario = args.scenario

temperature = 5.5
cooling = False

print(f"Starting ColdTrace simulator: {scenario}")


while True:

    # -------------------------
    # NORMAL SCENARIO
    # -------------------------
    if scenario == "normal":

        if cooling:
            temperature -= 0.18

            if temperature <= 5.8:
                cooling = False

        else:
            temperature += 0.08

            if temperature >= 7.5:
                cooling = True

    # -------------------------
    # HIGH TEMPERATURE
    # -------------------------
    elif scenario == "high_temp":

        cooling = True
        temperature += 0.12

    # -------------------------
    # LOW TEMPERATURE
    # -------------------------
    elif scenario == "low_temp":

        cooling = True
        temperature -= 0.25

    # -------------------------
    # RAPID TEMPERATURE RISE
    # -------------------------
    elif scenario == "rapid_rise":

        cooling = True
        temperature += 0.45

    # -------------------------
    # COOLING FAILURE
    # -------------------------
    elif scenario == "cooling_failure":

        cooling = True
        temperature += 0.20

    # Small sensor variation
    temperature += random.uniform(-0.03, 0.03)

    payload = {
        "device_id": "CT001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": round(temperature, 2),
        "humidity": round(
            58 + random.uniform(-1.5, 1.5),
            1
        ),
        "cooling": cooling
    }

    try:
        r = requests.post(
            URL,
            json=payload,
            timeout=3
        )

        print(
            payload,
            "->",
            r.json()
        )

    except requests.RequestException as e:
        print("Backend unavailable:", e)

    time.sleep(2)