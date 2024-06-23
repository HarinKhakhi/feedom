import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import { motion, AnimatePresence } from "framer-motion";
import Loader from "./Loader.jsx";

const BACKEND_URL = "http://localhost:8000";

const VideoPlayer = () => {
  const [videoIndex, setVideoIndex] = React.useState(-1);
  const [videos, setVideos] = React.useState([]);
  const [direction, setDirection] = React.useState(0);

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
    setDirection(1);
    if (videoIndex < videos.length - 1) {
      setVideoIndex(videoIndex + 1);
    }
  };

  const handlePreviousVideo = () => {
    setDirection(-1);
    if (videoIndex > 0) {
      setVideoIndex(videoIndex - 1);
    }
  };

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "ArrowRight") {
        handleNextVideo();
      } else if (event.key === "ArrowLeft") {
        handlePreviousVideo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleNextVideo, handlePreviousVideo]);

  if (videos.length === 0 || videoIndex === -1) {
    return <Loader message="Refining your feed..." />;
  }

  const variants = {
    enter: (direction) => ({
      x: direction > 0 ? window.innerWidth : -window.innerWidth,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction) => ({
      x: direction < 0 ? window.innerWidth : -window.innerWidth,
      opacity: 0,
    }),
  };

  return (
    <Box
      sx={{
        position: "relative",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        marginTop: "5px",
      }}
    >
      <AnimatePresence initial={false} custom={direction}>
        <motion.div
          key={videoIndex}
          custom={direction}
          variants={variants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          <Card
            sx={{
              width: "400px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <CardContent>
              {videos[videoIndex].title} {videoIndex}
            </CardContent>
            <CardMedia
              component="video"
              controls
              src={videos[videoIndex].video_id}
              title={videos[videoIndex].title}
              sx={{ height: 450 }}
            />
          </Card>
        </motion.div>
      </AnimatePresence>
    </Box>
  );
};

export default VideoPlayer;
