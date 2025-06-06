# AI_Powered_Self_Healing_Security_For_Connected_Vehicles

A Flask-based intelligent security system designed to detect and respond to anomalies in vehicle CAN bus communication using machine learning, natural language processing, and real-time data simulation.  
The system supports patch deployment, voice commands, and threat explanations to provide a self-healing automotive environment.

## OTIDS Dataset (CAN Dataset for Intrusion Detection)

The OTIDS (CAN Dataset for Intrusion Detection) is a dataset developed for evaluating intrusion detection systems (IDS) in Controller Area Network (CAN) bus communications within vehicles. The CAN protocol facilitates real-time data exchange among electronic control units (ECUs) in vehicles, but its design lacks source and destination address information, making it susceptible to unauthorized message injections that can lead to system malfunctions.

### Dataset Files

The OTIDS dataset includes several text files containing raw CAN bus data, attack scenarios, and metadata. Below are the filenames for the included text files:


- **Attack_free_dataset.txt**  
  Contains data from normal vehicle operations without any attack.

- **DoS_attack_dataset.txt**  
  Data representing Denial of Service (DoS) attacks on the CAN bus.

- **Fuzzy_attack_dataset.txt**  
  Data representing fuzzy attacks on the CAN bus.

- **Impersonation_attack_dataset.txt**  
  Data representing impersonation attacks on the CAN bus.

## Overview

This Flask-based application simulates a connected vehicle's CAN bus environment, detects anomalies in real time using a trained machine learning model, explains threats using a GPT-like interface, supports voice-based interaction through Whisper, and deploys simulated patches to respond to attacks. A live dashboard displays vehicle health, threats, and patch history.

## System Architecture

- Real-time CAN data is generated and monitored
- ML model detects anomalies
- Threats are logged with explanations
- Patch suggestions are generated and deployed
- Audio input can be transcribed using Whisper
- Text-to-speech available for verbal feedback
- All data is served via Flask REST API endpoints

## Key Features

- Real-time CAN data simulation and visualization
- Anomaly detection using trained ML model
- Threat explanation and logging
- Patch suggestion and simulated deployment
- Voice command support via Whisper (Speech-to-Text)
- Text-to-speech feedback system
- Historical logs and threat records
- GPT-like chatbot interface for threat-related queries

## API Endpoints

| Method | Endpoint            | Description                            |
|--------|---------------------|----------------------------------------|
| GET    | /vehicle_data       | Returns current CAN data               |
| POST   | /detect             | Sends CAN data to detect anomalies     |
| GET    | /history            | Fetch general event history            |
| GET    | /threat             | Fetch recent threat detections         |
| POST   | /transcribe         | Uploads audio file, returns transcript |
| POST   | /tts                | Converts text to speech (returns .wav) |
| POST   | /apply_patch        | Deploys simulated patch for a threat   |
| POST   | /generate-response  | GPT-style response to user questions   |
| GET    | /health             | Returns system status (health check)   |

## Installation & Setup

1. Clone the repository
2. Set up a virtual environment:
3. Install requirements:
4. Run the Flask app: python app.py

## ML Model Info

- Model: Random Forest Classifier
- Trained on: OTIDS Dataset
- Features used: CAN ID, DLC, bytes 0-7
- Output: Binary classification (normal / anomaly)

## Project Structure
self_healing_ai_patch/           # Root project folder
│
├── backend/                     # Backend system (Flask API, AI processing)
│   ├── app.py                   # Main Flask app (handles /detect, /history)
│   ├── can_data.py              # CAN bus data processing (loads OTIDS dataset)
│   ├── anomaly_detector.py      # Isolation Forest for anomaly detection
│   ├── gpt_threat.py            # GPT for threat explanation & simulation
│   ├── auto_patch.py            # AI-generated patch suggestions
│   ├── whisper_tts.py           # Voice interface (Whisper + Text-to-Speech)
│   ├── history_logger.py        # Logs detected threats into SQLite
│   ├── requirements.txt         # Backend dependencies (Flask, OpenAI, SciKit-Learn)
│
├── frontend/                    # Frontend system (Streamlit dashboard)
│   ├── dashboard.py             # Streamlit UI (fetches /detect + /history)
│   ├── styles.py                # UI styling (color codes, fonts)
│   ├── requirements.txt         # Frontend dependencies (Streamlit, Requests)
│
├── data/                        # Raw & processed datasets
│   ├── otids.csv                # OTIDS CAN dataset (real-world vehicle data)
│   ├── processed_data.csv       # Preprocessed data for anomaly detection
│
├── logs/                        # Threat detection logs
│   ├── threats.sqlite           # SQLite database storing detected threats
│   ├── sample_logs.txt          # Sample log outputs for debugging
│
└── .gitignore                   # Git ignore rules



