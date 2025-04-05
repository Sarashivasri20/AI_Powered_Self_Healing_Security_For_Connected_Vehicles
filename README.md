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



  