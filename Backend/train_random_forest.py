import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier

def parse_can_file(file_path, label):
    """
    Parses a CAN dataset text file and returns a DataFrame with columns:
    [can_id, dlc, byte_0..byte_7, label]
    
    Each line is expected to follow the format:
    Timestamp: 180.170712  ID: 0081  000  DLC: 8  7f 84 62 00 00 00 00 8e
    """
    rows = []
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return pd.DataFrame()

    print(f"🔎 Parsing {file_path} with label={label}")

    with open(file_path, "r") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split()

            if len(parts) < 7:
                if line_no <= 5 or line_no % 100000 == 0:
                    print(f"[DEBUG] Skipping line {line_no} (too short)")
                continue

            try:
                can_id = int(parts[3], 16)
                dlc = int(parts[6])
                data_bytes = parts[7:7 + dlc]
                byte_values = [int(b, 16) for b in data_bytes]

                # Pad to 8 bytes
                while len(byte_values) < 8:
                    byte_values.append(0)

                row = [can_id, dlc] + byte_values + [label]
                rows.append(row)

                if line_no <= 5 or line_no % 100000 == 0:
                    print(f"[DEBUG] Parsed line {line_no}")

            except Exception as e:
                if line_no <= 5 or line_no % 100000 == 0:
                    print(f"[DEBUG] Failed to parse line {line_no}: {e}")
                continue

    df = pd.DataFrame(rows, columns=["can_id", "dlc"] + [f"byte_{i}" for i in range(8)] + ["label"])
    print(f"✅ Parsed {len(df)} rows from {file_path}")
    return df


def train_random_forest():
    """
    Loads CAN datasets, labels them, trains a RandomForestClassifier,
    and saves the trained model.
    """
    df_attack_free = parse_can_file("../data/Attack_free_dataset.txt", label=0)
    df_dos         = parse_can_file("../data/DoS_attack_dataset.txt", label=1)
    df_fuzzy       = parse_can_file("../data/Fuzzy_attack_dataset.txt", label=1)
    df_imp         = parse_can_file("../data/Impersonation_attack_dataset.txt", label=1)

    all_data = pd.concat([df_attack_free, df_dos, df_fuzzy, df_imp], ignore_index=True)

    if all_data.empty:
        print("❌ No valid data found across all datasets. Exiting.")
        return

    print(f"📊 Total samples: {len(all_data)}")

    # Split into features and labels
    feature_cols = ["can_id", "dlc"] + [f"byte_{i}" for i in range(8)]
    X = all_data[feature_cols]
    y = all_data["label"]

    print("🧠 Training Random Forest for anomaly classification...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    output_path = os.path.join(".\\model", "random_forest_model.pkl")
    os.makedirs("model", exist_ok=True)
    joblib.dump(model, output_path)

    print(f"✅ Model saved to {output_path}")


if __name__ == "__main__":
    train_random_forest()