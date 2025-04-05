import requests
import time
import sys
import re

# ✅ Function to extract 8 CAN bytes from a line
def parse_can_line(line):
    try:
        if "Timestamp:" not in line or "DLC:" not in line:
            return None

        matches = re.findall(r'\b[0-9a-fA-F]{2}\b', line)
        if len(matches) >= 8:
            return {f"byte_{i}": int(matches[i], 16) for i in range(8)}
    except:
        return None

# ✅ Stream function
def stream_dataset(filepath, delay=0.2):
    with open(filepath, 'r') as f:
        print(f"🚗 Starting stream from: {filepath}")
        for line in f:
            data = parse_can_line(line)
            if not data:
                continue

            try:
                response = requests.post("http://127.0.0.1:5000/detect", json=data)
                result = response.json()
                print(f"📤 Sent: {data}")
                print(f"🧠 Result: {result['result']}")

                if result["result"] == "anomaly":
                    print(f"⚠️ Threat Explanation: {result['gpt_explanation']}")
                    print(f"🔧 Suggested Patch: {result['suggested_patch']}\n")

                time.sleep(delay)  # Simulate real-time data flow
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

import re

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stream_simulator.py [dataset_file.txt]")
    else:
        stream_dataset(sys.argv[1])
