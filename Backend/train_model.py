import os
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

def extract_features_from_file(filepath):
    rows = []
    with open(filepath, "r") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue  # skip blank lines

            # Debug: show each line
            #print(f"[DEBUG] Line {line_no}: {line}")

            parts = line.split()
            # we have:
            #  0 => "Timestamp:"
            #  1 => "175.950798"
            #  2 => "ID:"
            #  3 => "0081"
            #  4 => "000"
            #  5 => "DLC:"
            #  6 => "8"
            #  7.. -> data bytes

            # We need at least 8 parts for ID, DLC, some data
            if len(parts) < 7:
                print(f"[DEBUG] Skipping line {line_no}: too few parts ({len(parts)})")
                continue

            try:
                # can_id in parts[3]
                can_id_hex = parts[3]      # e.g. "0081"
                can_id = int(can_id_hex, 16)

                # skip parts[4], it's "000" in your logs
                # next is parts[5] = "DLC:", so we skip that text
                # parts[6] = the actual DLC number
                dlc = int(parts[6])        # "8"

                # data bytes at parts[7..(7+dlc)]
                data_bytes = parts[7 : 7 + dlc]
                byte_values = [int(b, 16) for b in data_bytes]

                # pad to 8 bytes if needed
                while len(byte_values) < 8:
                    byte_values.append(0)

                row = [can_id, dlc] + byte_values
                rows.append(row)

            except Exception as e:
                print(f"[DEBUG] Failed parsing line {line_no} -> {e}")
                continue

    return pd.DataFrame(
        rows,
        columns=["can_id", "dlc"] + [f"byte_{i}" for i in range(8)]
    )

def train_anomaly_model():
    dataset_files = [
        "../data/Attack_free_dataset.txt",
        "../data/DoS_attack_dataset.txt",
        "../data/Fuzzy_attack_dataset.txt",
        "../data/Impersonation_attack_dataset.txt"
    ]

    all_data = []
    for file in dataset_files:
        if os.path.exists(file):
            print(f"🔍 Extracting from {file}...")
            df = extract_features_from_file(file)
            if not df.empty:
                all_data.append(df)
                print(f"✅ {len(df)} rows extracted from {file}")
            else:
                print(f"⚠ No valid rows in {file}")
        else:
            print(f"❌ File not found: {file}")

    if not all_data:
        print("🚫 No valid data. Exiting.")
        return

    df = pd.concat(all_data, ignore_index=True)
    print(f"📊 Total training samples: {len(df)}")

    print("🧠 Training Isolation Forest...")
    contamination_rate = 0.03
    model = IsolationForest(
        contamination=contamination_rate,
        random_state=42
    )
    model.fit(df)

    joblib.dump(model, "./model/anomaly_model.pkl")
    print("✅ Model trained & saved as anomaly_model.pkl")

if __name__ == "__main__":

    train_anomaly_model()