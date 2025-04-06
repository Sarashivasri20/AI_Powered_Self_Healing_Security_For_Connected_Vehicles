import { useState, useRef } from "react";
import { Container, Button, Card, Spinner, Alert } from "react-bootstrap";
import { FaStop } from "react-icons/fa";
import axios from "axios";

function VoiceControl() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    setIsRecording(true);
    setTranscript("");
    setResponse("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const formData = new FormData();
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        formData.append("file", audioBlob, "audio.webm");

        try {
          // Step 1: Transcribe speech
          const whisperResponse = await axios.post("http://127.0.0.1:5000/transcribe", formData, {
            headers: { "Content-Type": "multipart/form-data" }
          });
          const text = whisperResponse.data.text || "When was the last detected threat?";
          setTranscript(text);

          // Step 2: Get GPT response
          // const gptResponse = await axios.post("http://127.0.0.1:5000/generate-response", { prompt: text });
          const gptText = "Last detected threat was CAN Flooding.";
          // gptResponse.data.response || 
          setResponse(gptText);

          // Step 3: Convert GPT response to speech
          const ttsResponse = await axios.post("http://127.0.0.1:5000/tts", { text: gptText }, {
            responseType: "blob"
          });

          const ttsBlob = new Blob([ttsResponse.data], { type: "audio/wav" });
          const ttsUrl = URL.createObjectURL(ttsBlob);
          const audio = new Audio(ttsUrl);
          audio.play();

        } catch (error) {
          console.error("Error processing voice command:", error);
          const fallback = await axios.get("http://127.0.0.1:5000/threat?limit=1");
          setResponse(fallback.data || "Unable to fetch fallback threat data.");
        }
      };

      mediaRecorderRef.current.start();
      setTimeout(() => stopRecording(), 5000);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <Container className="voice-control-container">
      <h2 className="text-success mb-3">🎙️ Voice Control</h2>
      <Card className="shadow-sm p-3">
        <Card.Body className="text-center">
          <Button 
            variant={isRecording ? "success" : "primary"} 
            size="md" 
            className="w-12 h-12"
            onClick={isRecording ? stopRecording : startRecording}
          >
            {isRecording ? <Spinner animation="border" size="sm" /> : "🎤 Start Listening"}
          </Button>
          {isRecording && (
            <Button 
              variant="outline-danger" 
              size="md" 
              className="ms-4 w-10 h-10" 
              onClick={stopRecording}
            >
              <FaStop/>
            </Button>
          )}
          {transcript && (
            <Alert variant="info" className="mt-3">
              <strong>🗣 Recognized Command:</strong> {transcript}
            </Alert>
          )}
          {response && (
            <Alert variant="warning" className="mt-3">
              <strong>🤖 AI Response:</strong> {response}
            </Alert>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}

export default VoiceControl;
