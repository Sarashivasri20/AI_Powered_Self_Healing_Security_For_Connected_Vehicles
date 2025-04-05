from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import joblib
import random
import time
import threading
import os

# Your modules
from history_logger import log_threat, fetch_threat_history, fetch_history, get_threat, log_patch
from whisper_tts import transcribe_audio, generate_speech

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load trained anomaly detection model
model = joblib.load("./model/random_forest_model.pkl")

# Global vehicle data
current_vehicle_data = {}

# Generate random simulated CAN data
import random

def generate_can_data():
    # 70% chance of healthy, 30% chance of anomaly
    is_healthy = random.random() < 0.7

    if is_healthy:
        data = {
            "vehicle_id": f"Vehicle_001",
            "can_id": random.randint(0x100, 0x7FF),
            "dlc": random.randint(1, 8),
            "byte_0": random.randint(800, 3000),     # RPM
            "byte_1": random.randint(0, 60),         # Throttle %
            "byte_2": random.randint(0, 100),        # Brake Pressure
            "byte_3": random.randint(-20, 20),       # Steering Angle
            "byte_4": random.randint(0, 120),        # Speed km/h
            "byte_5": random.randint(30, 80),        # Fuel %
            "byte_6": round(random.uniform(11.5, 13.5), 2),  # Battery Voltage
            "byte_7": random.randint(1, 5),          # Gear
        }
    else:
        data = {
            "vehicle_id": f"Vehicle_001",
            "can_id": random.randint(0x100, 0x7FF),
            "dlc": random.randint(1, 8),
            "byte_0": random.randint(7000, 9000),    # High RPM
            "byte_1": random.randint(90, 100),       # Throttle maxed
            "byte_2": random.randint(200, 255),      # Brake to max
            "byte_3": random.randint(-90, 90),       # Wild steering
            "byte_4": random.randint(180, 250),      # Over-speeding
            "byte_5": random.randint(0, 5),          # Fuel nearly empty
            "byte_6": round(random.uniform(5.0, 9.0), 2),   # Low battery
            "byte_7": random.randint(5, 6),          # High gear at low speed
        }

    print("🔁 Generated CAN data:", "Healthy" if is_healthy else "Anomalous", data)
    return data


# Background thread to simulate real-time CAN data
def update_vehicle_data():
    global current_vehicle_data
    while True:
        current_vehicle_data = generate_can_data()
        time.sleep(20)

# Detect anomalies in CAN packets
@app.route('/detect', methods=['POST'])
def detect():
    try:
        data = request.get_json()
        features_dict = {
            "can_id": data["can_id"],
            "dlc": data["dlc"],
            **{f"byte_{i}": data.get(f"byte_{i}", 0) for i in range(8)}
        }
        features_df = pd.DataFrame([features_dict])
        prediction = model.predict(features_df)[0]
        print("🔍 Anomaly detection result:", prediction)

        gpt_explanation = "Potential attack detected in vehicle CAN network." if prediction == 1 else None
        patch = "Apply IDS rule to monitor abnormal CAN packets." if prediction == 1 else None
        result = "anomaly" if prediction == 1 else "normal"
        attack = "CAN Flooding" if prediction == 1 else "No attack detected"

        print("🔍 Anomaly detection result:", prediction, "Attack type:", attack)

        if prediction == 1:
            # Log the threat with the GPT-like explanation
            log_threat(data["vehicle_id"], prediction, attack, gpt_explanation, patch)
        else:
            log_threat(data["vehicle_id"], prediction, "No anomaly detected", "No anomaly detected. System ready to go", "no patch needed at this stage")

        return jsonify({
            "result": result,
            "gpt_explanation": gpt_explanation,
            "suggested_patch": patch
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# Return current vehicle CAN data
@app.route('/vehicle_data', methods=['GET'])
def vehicle_data():
    print("📡 Sending vehicle data:", current_vehicle_data)
    return jsonify(current_vehicle_data)

# Return recent history
@app.route('/history', methods=['GET'])
def history():
    try:
        limit = request.args.get('limit', default=10, type=int)
        history_data = fetch_history(limit)
        print(history_data)
        return jsonify({"history": history_data})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Return recent threats    
@app.route('/threat', methods=['GET'])
def threat():
    try:
        limit = request.args.get('limit', default=10, type=int)
        history_data = fetch_threat_history(limit)
        print(history_data)
        return jsonify({"history": history_data})
    except Exception as e:
        return jsonify({"error": str(e)})

# Transcribe audio using Whisper
@app.route('/transcribe', methods=['POST'])
def whisper_transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']
    filename = audio_file.filename
    audio_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        audio_file.save(audio_path)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {e}'}), 500

    transcription = transcribe_audio(audio_path)

    if os.path.exists(audio_path):
        os.remove(audio_path)

    return jsonify({'transcription': transcription})

# Text to speech
@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get("text", "No input provided.")
        output_path = os.path.join(UPLOAD_FOLDER, "output_speech.wav")
        generate_speech(text, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

# Simulated patch deployment
@app.route('/apply_patch', methods=['POST'])
def apply_patch():
    try:
        data = request.get_json()
        timestamp = data.get("timestamp", None)  # Frontend provides timestamp

        if not timestamp:
            return jsonify({"error": "Timestamp is required to fetch the correct threat log."})

        last_threat = get_threat(timestamp)

        if not last_threat:
            return jsonify({"error": f"No threat log found for at {timestamp}."})

        anomaly_score, attack, suggested_patch = last_threat

        # 🚗 Determine the patch based on the attack type
        patch_message = generate_patch(attack, suggested_patch)

        # Store applied patch
        log_patch(patch_message)

        # 🚗 Convert patch message into a byte payload (simulating a firmware update)
        can_patch = {f"byte_{i}": ord(c) % 256 for i, c in enumerate(patch_message[:8])}
        print(f"🚗 Sending patch : {can_patch}")

        return jsonify({
            "status": f"Patch sent",
            "original_anomaly": {
                "attack": attack,
                "suggested_patch": suggested_patch,
                "anomaly_score": anomaly_score,
                "timestamp": timestamp
            },
            "patch_applied": patch_message,
            "patch_data": can_patch,
        })

    except Exception as e:
        return jsonify({"error": str(e)})



# Simulated GPT-like chatbot response
@app.route('/generate-response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        user_input = data.get("input", "No input provided.")

        simulated_responses = {
            "What was the last detected threat?": "The last detected threat was an ECU Tampering attack.",
            "How do I secure my CAN network?": "Implement an Intrusion Detection System and encrypt CAN messages.",
            "What is anomaly detection?": "Anomaly detection identifies patterns that deviate from expected behavior.",
        }

        response = simulated_responses.get(user_input, "The last detected threat was an ECU Tampering attack.")
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)})

# Optional: Health check route
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK"})

# Start everything
if __name__ == '__main__':
    # Start the background CAN data simulation thread
    threading.Thread(target=update_vehicle_data, daemon=True).start()
    
    # Run the Flask app without auto-reloader (to avoid thread issues)
    app.run(debug=True, use_reloader=False, host="localhost", port=5000)
