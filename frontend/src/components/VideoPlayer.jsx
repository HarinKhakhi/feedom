import React, { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Loader from "./Loader.jsx";
import ReactPlayer from "react-player";

const BACKEND_URL = "http://localhost:8000";

const VideoPlayer = () => {
  const [videoIndex, setVideoIndex] = React.useState(-1);
  const [videoIds, setVideoIds] = React.useState([]);
  const [videos, setVideos] = React.useState({});
  const [direction, setDirection] = React.useState(0);

  useEffect(() => {
    fetch(`${BACKEND_URL}/feed`)
      .then((response) => response.json())
      .then((data) => {
        let URLs = {};
        for (let videoId of data) {
          URLs[videoId] = `videos/${videoId}`;
        }
        setVideos(URLs);
        setVideoIds(data);
        setVideoIndex(0);
      })
      .catch((error) => console.error("Error fetching video IDs:", error));
  }, []);

  const handleNextVideo = async () => {
    setDirection(1);
    if (videoIndex < videoIds.length - 1) {
      setVideoIndex(videoIndex + 1);
    }
  };

  const handlePreviousVideo = async () => {
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
  }, [videoIndex, videoIds.length]);

  if (videoIndex === -1 || videos[videoIds[videoIndex]] === undefined) {
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
    <div
      style={{
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
          <div
            style={{
              width: "400px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <div>Placeholder Title: {videoIndex}</div>
            <ReactPlayer
              controls={true}
              url={videos[videoIds[videoIndex]]}
              width="100%"
              height="100%"
            />
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default VideoPlayer;
