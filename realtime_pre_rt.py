import serial
import joblib
import numpy as np
import pandas as pd
import time
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
PORT            = 'COM5'
BAUD            = 115200
OVERHEAT_LIMIT  = 50.0
HYSTERESIS      = 2.0

THRESH_PELTIER  = 50.0
THRESH_FAN_HIGH = 45.0
THRESH_FAN_LOW  = 40.0
THRESH_OFF      = 35.0

LEVEL_RANK = {"OFF": 0, "FAN_LOW": 1, "FAN_HIGH": 2, "PELTIER": 3}

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────
print("Connecting to ESP32...")
ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)
print("Connected!")

print("Loading ML model...")
model  = joblib.load("temp_model.pkl")
scaler = joblib.load("scaler.pkl")
print("Model loaded!")

prev_temp         = None
cooling_level     = "OFF"
prev_level        = "OFF"
step              = 0
rise_rate_history = []   # for smoothing

# ─────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────
def decide_cooling(predicted_temp, temp_rate, current_level):
    # Step UP thresholds — raise rate threshold to ignore small noise
    if predicted_temp > THRESH_PELTIER or temp_rate > 2.0:
        new_level = "PELTIER"
    elif predicted_temp > THRESH_FAN_HIGH or temp_rate > 1.0:
        new_level = "FAN_HIGH"
    elif predicted_temp > THRESH_FAN_LOW:
        new_level = "FAN_LOW"
    else:
        new_level = "OFF"

    current_rank = LEVEL_RANK[current_level]
    new_rank     = LEVEL_RANK[new_level]

    # Hysteresis on step DOWN only
    if new_rank < current_rank:
        if predicted_temp < (THRESH_OFF - HYSTERESIS) and temp_rate <= 0:
            return "OFF"
        elif predicted_temp < (THRESH_FAN_LOW - HYSTERESIS):
            return "FAN_LOW"
        elif predicted_temp < (THRESH_FAN_HIGH - HYSTERESIS):
            return "FAN_HIGH"
        else:
            return current_level
    else:
        return new_level

def estimate_time_to_overheat(max_temp, temp_rate, limit=OVERHEAT_LIMIT):
    if temp_rate <= 0:
        return float('inf')
    remaining = limit - max_temp
    if remaining <= 0:
        return 0.0
    return round(remaining / temp_rate, 1)

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
print("\nStarting thermal management loop...\n")
print("=" * 50)

while True:
    try:
        line = ser.readline().decode('utf-8').strip()

        if not line:
            continue

        values = line.split(",")
        if len(values) != 5:
            print(f"[WARN] Unexpected data: {line}")
            continue

        T1      = float(values[0])
        T2      = float(values[1])
        T3      = float(values[2])
        current = float(values[3])
        voltage = float(values[4])

        step += 1
        max_temp = max(T1, T2, T3)
        hot_cell = ["T1","T2","T3"][[T1,T2,T3].index(max_temp)]

        # ── Rise Rate (smoothed over last 3 readings) ──────
        if prev_temp is None:
            prev_temp = max_temp
            temp_rate = 0.0
        else:
            temp_rate = round(max_temp - prev_temp, 3)
            prev_temp = max_temp

        rise_rate_history.append(temp_rate)
        if len(rise_rate_history) > 3:
            rise_rate_history.pop(0)
        smoothed_rate = round(sum(rise_rate_history) / len(rise_rate_history), 3)

        # ── ML Prediction ──────────────────────────────────
        features = pd.DataFrame(
            [[T1, T2, T3, current, voltage, smoothed_rate]],
            columns=["T1","T2","T3","Current","Voltage","rise_rate"]
        )
        features_scaled = scaler.transform(features)
        predicted_temp  = round(model.predict(features_scaled)[0], 2)

        # ── Time to Overheat ───────────────────────────────
        tte = estimate_time_to_overheat(max_temp, smoothed_rate)
        tte_str = f"{tte}s" if tte != float('inf') else "Safe"

        # ── Cooling Decision ───────────────────────────────
        cooling_level = decide_cooling(predicted_temp, smoothed_rate, cooling_level)

        # ── Send to ESP32 ──────────────────────────────────
        ser.write((cooling_level + "\n").encode())

        # ── Print Status ───────────────────────────────────
        changed = "  ◄ CHANGED" if cooling_level != prev_level else ""
        prev_level = cooling_level

        print(f"Step {step:04d}")
        print(f"  Temps        : T1={T1}°C  T2={T2}°C  T3={T3}°C")
        print(f"  Hottest      : {hot_cell} = {max_temp}°C")
        print(f"  Rise Rate    : {smoothed_rate}°C/s  (smoothed)")
        print(f"  Predicted    : {predicted_temp}°C")
        print(f"  Overheat in  : {tte_str}")
        print(f"  Cooling      : {cooling_level}{changed}")

        if max_temp >= OVERHEAT_LIMIT:
            print(f"  🚨 CRITICAL! {hot_cell} at {max_temp}°C — MAX COOLING!")
        elif tte != float('inf') and tte < 10:
            print(f"  ⚠️  WARNING: Overheat in {tte}s!")

        print("-" * 50)

    except serial.SerialException as e:
        print(f"[SERIAL ERROR] {e}")
        time.sleep(3)
        try:
            ser.close()
            ser = serial.Serial(PORT, BAUD, timeout=2)
            print("Reconnected!")
        except:
            print("Reconnect failed. Check USB cable.")

    except ValueError as e:
        print(f"[PARSE ERROR] {line} → {e}")

    except KeyboardInterrupt:
        print("\nStopping...")
        ser.write(("OFF\n").encode())
        ser.close()
        print("Cooling OFF. Bye!")
        break