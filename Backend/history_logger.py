import sqlite3

DB_FILE = "../logs/threats.sqlite"

def init_db():
    """Create threats table if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            vehicle_id TEXT,
            anomaly_score REAL,
            attack TEXT,
            gpt_explanation TEXT,
            suggested_patch TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_threat(vehicle_id, anomaly_score, attack, gpt_explanation, suggested_patch):
    """Log a detected security threat into the database, ensuring anomaly_score is stored as a float."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        anomaly_score = float(anomaly_score)  # Ensure it's a float before inserting
    except ValueError:
        anomaly_score = 1.0  # Default value for invalid data

    cursor.execute('''
        INSERT INTO threats (timestamp, vehicle_id, anomaly_score, attack, gpt_explanation, suggested_patch)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
    ''', (vehicle_id, anomaly_score, attack, gpt_explanation, suggested_patch))

    conn.commit()
    print(f"Threat logged: {vehicle_id}, {anomaly_score}, {attack}, {gpt_explanation}, {suggested_patch}")
    conn.close()


def fetch_history(limit=10):
    """Retrieve the last N detected threats."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, timestamp, vehicle_id, anomaly_score, attack, gpt_explanation, suggested_patch FROM threats ORDER BY timestamp DESC LIMIT ?', (limit,))
    
    # Fetch column names
    columns = [desc[0] for desc in cursor.description]

    # Convert rows to dictionaries
    history = []
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))

        # Ensure anomaly_score is always a float
        try:
            row_dict["anomaly_score"] = float(row_dict["anomaly_score"])
        except (ValueError, TypeError):
            row_dict["anomaly_score"] = 1.0  # Default fallback value

        history.append(row_dict)

    conn.close()
    return history

def fetch_threat_history(limit=10):
    """Retrieve the last N detected threats with anomaly_score set to -1."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, vehicle_id, anomaly_score, attack, gpt_explanation, suggested_patch 
        FROM threats 
        WHERE anomaly_score = -1 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    # Fetch column names
    columns = [desc[0] for desc in cursor.description]

    # Convert rows to dictionaries
    history = []
    for row in cursor.fetchall():
        row_dict = dict(zip(columns, row))
        history.append(row_dict)

    conn.close()
    return history

def patch_logger():
    """Create applied_patches table if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applied_patches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            vehicle_id TEXT,
            patch TEXT
        )
    ''')

    conn.commit()
    conn.close()

def log_patch(patch):
    """Log a patch applied to a vehicle."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applied_patches (timestamp, "001", patch)
        VALUES (datetime('now'), ?, ?)
    ''', (patch))

    conn.commit()
    print(f"Patch logged: {patch}")
    conn.close()

def get_threat(timestamp):
    """Fetch the most recent threat for a vehicle."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT anomaly_score, attack, suggested_patch FROM threats
        WHERE vehicle_id = 001
        AND timestamp = ?
    ''', (timestamp,))
    
    last_threat = cursor.fetchone()
    conn.close()
    
    return last_threat if last_threat else None


# init_db()
# patch_logger()
# import random

# List of attack types and corresponding explanations and patches
# attack_types = [
#     ("DoS", "A DoS attack floods the CAN bus with high-priority messages, preventing normal communication.", 
#             "Activate the vehicle's security update to handle message overloads."),
#     ("Fuzzy", "A Fuzzy attack sends malformed or random data to confuse or crash ECUs.",
#             "Enable data validity checks to prevent unsafe reads."),
#     ("Impersonation", "An Impersonation attack uses spoofed IDs to mimic legitimate ECUs and inject malicious data.",
#             "Turn on ID verification to block unauthorized messages."),
#     ("Attack_free", "No attack detected. All vehicle systems appear to be operating normally.",
#             "No action needed – vehicle is normal.")
# ]

# # Manually log random threats with explanations and patches
# for _ in range(15):  # Log 5 random threats
#     attack_type, explanation, patch = random.choice(attack_types)
    
#     # Set anomaly score based on attack type
#     anomaly_score = -1 if attack_type != "Attack_free" else 1
    
#     # Log the threat for vehicle 001 (or any other vehicle ID)
#     log_threat(vehicle_id="001", anomaly_score=anomaly_score, attack=attack_type, 
#                gpt_explanation=explanation, suggested_patch=patch)



# if __name__ == "__main__":
#     print(fetch_history())