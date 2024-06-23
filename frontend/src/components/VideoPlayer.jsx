import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Loader from "./Loader.jsx";

const BACKEND_URL = "http://localhost:8000";

const VideoPlayer = () => {
  const [videoIndex, setVideoIndex] = React.useState(-1);
  const [videos, setVideos] = React.useState([]);

  useEffect(() => {
    fetch(`${BACKEND_URL}/feed`)
      .then((response) => response.json())
      .then((data) => {
        setVideos(data);
        if (data.length > 0) {
          setVideoIndex(0);
        }
      });
  }, []);

  const handleNextVideo = () => {
    if (videoIndex < videos.length - 1) {
      setVideoIndex(videoIndex + 1);
    }
  };

  const handlePreviousVideo = () => {
    if (videoIndex > 0) {
      setVideoIndex(videoIndex - 1);
    }
  };

  if (videos.length === 0 || videoIndex === -1) {
    return <Loader message="Refining your feed..." />;
  }

  return (
    <Box
      sx={{
        position: "relative",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        marginTop: 5,
      }}
    >
      <Button
        variant="contained"
        color="primary"
        onClick={handlePreviousVideo}
        disabled={videoIndex === 0}
        sx={{ marginRight: 3 }}
      >
        Previous
      </Button>
      <Card sx={{ maxWidth: 800, display: "flex", flexDirection: "column" }}>
        <CardMedia
          component="video"
          controls
          src={videos[videoIndex].video_id}
          title={videos[videoIndex].title}
          sx={{ height: 450 }}
        />
      </Card>
      <Button
        variant="contained"
        color="primary"
        onClick={handleNextVideo}
        disabled={videoIndex === videos.length - 1}
        sx={{ marginLeft: 3 }}
      >
        Next
      </Button>
    </Box>
  );
};

export default VideoPlayer;
