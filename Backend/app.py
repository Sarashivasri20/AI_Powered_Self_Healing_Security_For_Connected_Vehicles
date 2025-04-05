from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
import joblib
import random
import time
import threading
import os
import re

# Your modules
from history_logger import log_threat, fetch_threat_history, fetch_history, log_patch
from whisper_tts import transcribe_audio, generate_speech
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from g_model import getResponse

# Load model and tokenizer the Hugging Face way
model = GPT2LMHeadModel.from_pretrained("./model/fine_tuned_distilgpt2")
tokenizer = GPT2Tokenizer.from_pretrained("./model/fine_tuned_distilgpt2")

# Create the text generation pipeline
gpt2_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load trained anomaly detection model
# model = joblib.load("./model/random_forest_model.pkl")
model = joblib.load("./model/anomaly_model.pkl")

# Global vehicle data
current_vehicle_data = {}

# Generate random simulated CAN data
import random

#parse the gpt output
def parse_gpt_output(output):
    """
    Extracts attack type, explanation, and patch from GPT-2 response text.
    Assumes response is in format:
    Attack Type: XYZ
    Explanation: ...
    Suggested Patch: ...
    """
    attack_type = ""
    explanation = ""
    patch = ""

    # Normalize newlines
    lines = output.strip().split("\n")
    combined_output = " ".join(lines)

    # Regex patterns
    attack_match = re.search(r"Attack Type:\s*(.*?)(?:Explanation:|Suggested Patch:|$)", combined_output, re.IGNORECASE)
    explanation_match = re.search(r"Explanation:\s*(.*?)(?:Suggested Patch:|Attack Type:|$)", combined_output, re.IGNORECASE)
    patch_match = re.search(r"Suggested Patch:\s*(.*)", combined_output, re.IGNORECASE)

    if attack_match:
        attack_type = attack_match.group(1).strip()

    if explanation_match:
        explanation = explanation_match.group(1).strip()

    if patch_match:
        patch = patch_match.group(1).strip()

    return {
        "attack_type": attack_type,
        "explanation": explanation,
        "patch": patch
    }

# Function to encode patch text into CAN byte-style format
def encode_patch_to_can(patch_text):
    patch_text = patch_text.lower()

    if "ids" in patch_text and "monitor" in patch_text:
        return {
            "byte_0": 0x02,  # ENABLE_IDS
            "byte_1": 0xB1,  # CAN_MONITOR
            "byte_2": 0x01,  # ACTIVE_MONITORING
            "byte_3": 0x00,
            "byte_4": 0x00,
            "byte_5": 0x00,
            "byte_6": 0x00,
            "byte_7": 0x00
        }

    elif "security update" in patch_text and "overload" in patch_text:
        return {
            "byte_0": 0x03,  # THROTTLING MODE
            "byte_1": 0xA2,  # NETWORK CONTROL MODULE
            "byte_2": 0x02,  # OVERLOAD HANDLER
            "byte_3": 0x00,
            "byte_4": 0x00,
            "byte_5": 0x00,
            "byte_6": 0x00,
            "byte_7": 0x00
        }

    elif "data validity" in patch_text:
        return {
            "byte_0": 0x04,  # VALIDATION MODULE
            "byte_1": 0xC3,
            "byte_2": 0x01,
            "byte_3": 0x00,
            "byte_4": 0x00,
            "byte_5": 0x00,
            "byte_6": 0x00,
            "byte_7": 0x00
        }

    elif "id verification" in patch_text:
        return {
            "byte_0": 0x05,  # AUTH MODULE
            "byte_1": 0xD4,
            "byte_2": 0x01,
            "byte_3": 0x00,
            "byte_4": 0x00,
            "byte_5": 0x00,
            "byte_6": 0x00,
            "byte_7": 0x00
        }

    # Default: fallback — encode first 8 characters
    return {f"byte_{i}": ord(c) % 256 for i, c in enumerate(patch_text[:8])}


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

        # Extract bytes
        bytes_list = [data.get(f"byte_{i}", 0) for i in range(8)]
        can_id = data["can_id"]
        dlc = data["dlc"]

        # For IsolationForest input
        features_dict = {
            "can_id": can_id,
            "dlc": dlc,
            **{f"byte_{i}": bytes_list[i] for i in range(8)}
        }

        features_df = pd.DataFrame([features_dict])
        prediction = model.predict(features_df)[0]
        print("🔍 Anomaly detection result:", prediction)

        if prediction == -1:
            # Generate the prompt with only the CAN data
            prompt = f"CAN ID: {can_id}, DLC: {dlc}, Data: {bytes_list}\n"

            # Tokenize the input prompt
            inputs = tokenizer(prompt, return_tensors="pt")

            # Generate response from the fine-tuned model
            outputs = model.generate(
                **inputs,
                max_length=256,
                do_sample=True,
                top_k=50,
                temperature=0.9,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )

            # Decode the generated output
            output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Parse the GPT output (assuming the format you expect)
            parsed = parse_gpt_output(output_text)
            attack = parsed["attack_type"]
            gpt_explanation = parsed["explanation"]
            patch = parsed["patch"]

            # Check if attack is unknown and retry if necessary
            if attack.lower() in ["unknown", "undefined", "not detected"]:
                print("🔴 Unknown attack detected. Retrying...")
                # Retry by adding more context
                prompt = f"""
                CAN ID: {can_id}, DLC: {dlc}, Data: {bytes_list}
                """
                inputs = tokenizer(prompt, return_tensors="pt")
                outputs = model.generate(
                    **inputs,
                    max_length=256,
                    do_sample=True,
                    top_k=50,
                    temperature=0.9,
                    repetition_penalty=1.2,
                    pad_token_id=tokenizer.eos_token_id
                )
                output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

                print(output_text)

                parsed = parse_gpt_output(output_text)
                attack = parsed["attack_type"]
                gpt_explanation = parsed["explanation"]
                patch = parsed["patch"]

            # If attack still unknown, handle gracefully
            if attack.lower() in ["unknown", "undefined", "not detected"]:
                attack = "Attack type could not be identified."
                gpt_explanation = "No valid attack explanation available."
                patch = "Unable to suggest a valid patch."

        else:
            attack = "No attack detected"
            gpt_explanation = "No anomaly detected. System ready to go."
            patch = "No patch needed"

        # Log for history
        log_threat(data["vehicle_id"], prediction, attack, gpt_explanation, patch)

        return jsonify({
            "result": "anomaly" if prediction == -1 else "normal",
            "attack_type": attack,
            "gpt_explanation": gpt_explanation,
            "suggested_patch": patch
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route('/g_detect', methods=['POST'])
def g_detect():
    try:
        data = request.get_json()

        # Extract bytes from the request data
        bytes_list = [data.get(f"byte_{i}", 0) for i in range(8)]
        can_id = data["can_id"]
        dlc = data["dlc"]

        # For IsolationForest input
        features_dict = {
            "can_id": can_id,
            "dlc": dlc,
            **{f"byte_{i}": bytes_list[i] for i in range(8)}
        }

        features_df = pd.DataFrame([features_dict])
        prediction = model.predict(features_df)[0]
        print("🔍 Anomaly detection result:", prediction)

        if prediction == -1:
            # Generate the prompt with only the CAN data
            prompt = f"CAN ID: {can_id}, DLC: {dlc}, Data: {bytes_list} Give the output in 3 lines, Attack Type: (one line max), Explanation:(one line max) and Suggested Patch: (one line max) Stick to the format strictly.\n"

            # First pass - Get response from GPT-2 based on CAN data
            g_output = getResponse(prompt)

            print("GPT-2 Output:", g_output)

            # Parse the GPT output into attack type, explanation, and patch
            parsed = parse_gpt_output(g_output)
            attack = parsed["attack_type"]
            gpt_explanation = parsed["explanation"]
            patch = parsed["patch"]
        else:
            attack = "No attack detected"
            gpt_explanation = "No anomaly detected. System ready to go."
            patch = "No patch needed"

        # Log threat data for history (Optional function)
        log_threat(data["vehicle_id"], prediction, attack, gpt_explanation, patch)

        return jsonify({
            "result": "anomaly" if prediction == -1 else "normal",
            "attack_type": attack,
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
        patch_text = data.get("patch", None)

        if not patch_text:
            return jsonify({"error": "Patch text is required."})

        # Step 1: Encode patch into CAN byte-style format
        can_patch = encode_patch_to_can(patch_text)

        # Step 2: Log the applied patch (optional, for history)
        log_patch(patch_text)
        print(patch_text)

        # Step 3: Return response
        return jsonify({
            "status": "Patch applied successfully.",
            "patch_applied": patch_text,
            "patch_data": can_patch
        })
    

    except Exception as e:
        return jsonify({"error": str(e)})


# Simulated GPT-like chatbot response
@app.route('/generate-response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        user_input = data.get("input", "No input provided.")

        #Use GPT-2 pipeline to generate a response
        gpt_output = gpt2_pipeline(user_input, max_length=100, num_return_sequences=1)[0]["generated_text"]

        return jsonify({"response": gpt_output.strip()})
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
