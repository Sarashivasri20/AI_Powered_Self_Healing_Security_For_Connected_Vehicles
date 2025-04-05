import pyttsx3
import os
import speech_recognition as sr
from pydub import AudioSegment

# Initialize TTS engine
tts_engine = pyttsx3.init()

def convert_audio(input_path, output_format="wav"):
    """Convert audio file to WAV format for compatibility with SpeechRecognition."""
    output_path = os.path.splitext(input_path)[0] + f".{output_format}"
    
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # Ensure compatibility
        audio.export(output_path, format=output_format)
        return output_path
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribe speech from an audio file using Google STT."""
    recognizer = sr.Recognizer()
    
    # Convert to WAV if necessary
    converted_path = convert_audio(audio_path) if not audio_path.endswith(".wav") else audio_path
    
    if not converted_path:
        return "Error: Audio conversion failed."
    
    try:
        with sr.AudioFile(converted_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Error: Could not understand the audio."
    except sr.RequestError as e:
        return f"Error: Could not request results from Google STT; {e}"
    except Exception as e:
        return f"Error transcribing audio: {e}"
    finally:
        # Delete the converted file if it was created
        if converted_path != audio_path and os.path.exists(converted_path):
            os.remove(converted_path)


def generate_speech(text, output_path="../data/output_speech.wav"):
    """Convert text to speech and save as an audio file."""
    try:
        tts_engine.save_to_file(text, output_path)
        tts_engine.runAndWait()
        return output_path
    except Exception as e:
        return f"Error generating speech: {e}"
