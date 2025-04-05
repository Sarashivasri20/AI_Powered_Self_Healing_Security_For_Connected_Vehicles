import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import '../styles/SearchComponent.css';

const SearchComponent = ({ setSearchQuery }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recorder, setRecorder] = useState(null);
  const [localQuery, setLocalQuery] = useState("");

  // Handle text input change
  const handleTextSearch = (e) => {
    const value = e.target.value;
    setLocalQuery(value);
    setSearchQuery(value);
  };

  // Handle voice search: send recorded audio to backend
  const handleVoiceSearch = async (audioBlob) => {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob);

      const response = await axios.post('/whisper', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.transcription) {
        // Update both local query and search query with the transcription result
        setLocalQuery(response.data.transcription);
        setSearchQuery(response.data.transcription);
      } else {
        console.error('No transcription received');
      }
    } catch (error) {
      console.error('Error in voice recognition:', error);
    }
  };

  // Start recording audio for voice search
  const startRecording = () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
          const mediaRecorder = new MediaRecorder(stream);
          setRecorder(mediaRecorder);
          const chunks = [];

          mediaRecorder.ondataavailable = (event) => {
            chunks.push(event.data);
          };

          mediaRecorder.onstop = () => {
            const audioBlob = new Blob(chunks, { type: 'audio/wav' });
            handleVoiceSearch(audioBlob);
          };

          mediaRecorder.start();
          setIsRecording(true);

          // Auto-stop after 5 seconds if not manually stopped
          setTimeout(() => {
            if (mediaRecorder.state !== 'inactive') {
              mediaRecorder.stop();
              setIsRecording(false);
            }
          }, 5000);
        })
        .catch((err) => console.error('Error accessing microphone:', err));
    }
  };

  // Stop recording manually
  const stopRecording = () => {
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="search-container">
      <div className="button-container">
        {!isRecording ? (
          <button className="record-button" onClick={startRecording}>
            <MicIcon fontSize="large" />
            <span>Start Voice Search</span>
          </button>
        ) : (
          <button className="record-button stop" onClick={stopRecording}>
            <StopIcon fontSize="large" />
            <span>Stop Recording</span>
          </button>
        )}
      </div>
      <TextField
        label="Search History"
        variant="outlined"
        value={localQuery}
        onChange={handleTextSearch}
        className="search-textfield"
      />
    </div>
  );
};

export default SearchComponent;
