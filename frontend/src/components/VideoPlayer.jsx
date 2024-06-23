import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";

import Loader from "./Loader.jsx";

const BACKEND_URL = "http://localhost:8000";

const VideoPlayer = ({ title, videoUrl }) => {
  const [videoIndex, setVideoIndex] = React.useState(-1);
  const [videos, setVideos] = React.useState([]);

  useEffect(() => {
    fetch(`${BACKEND_URL}/feed`)
      .then((response) => response.json())
      .then((data) => {
        setVideos(data.videos);
        setVideoIndex(0);
      });
  }, []);

  const handleNextVideo = () => {
    setVideoIndex(videoIndex + 1);
  };

  const handlePreviousVideo = () => {
    setVideoIndex(videoIndex - 1);
  };

  if (videos.length === 0) return <Loader message="Refining your feed..." />;

  return (
    <Card sx={{ maxWidth: 800, margin: "auto", mt: 5 }}>
      <CardMedia
        component="video"
        controls
        src={videos[videoIndex].url}
        title={videos[videoIndex].title}
        sx={{ height: 450 }}
      />
      <CardContent>
        <Typography variant="h5" component="div">
          {videos[videoIndex].title}
        </Typography>
      </CardContent>
      <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handlePreviousVideo}
          disabled={videoIndex == 0}
        >
          Previous
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleNextVideo}
          disabled={videoIndex == videos.length - 1}
        >
          Next
        </Button>
      </Box>
    </Card>
  );
};

export default VideoPlayer;
