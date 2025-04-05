import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';

const speakText = (text) => {
  const utterance = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(utterance);
};

export default function CardComponent({ item }) {
  return (
    <Card sx={{ maxWidth: 345, margin: '10px' }}>
      <CardActionArea>
        <CardMedia
          component="img"
          height="140"
          image="../assets/vehicle.jpg"
          alt="vehicle image"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="div">
            Date: {item.date}
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Anomaly Detected: {item.anomaly}
          </Typography>
          <button onClick={() => speakText(`On ${item.date}, ${item.anomaly}`)}>
            Read Aloud
          </button>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
