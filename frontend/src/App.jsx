import React, { useEffect, useState } from "react";
import SearchAppBar from "./components/SearchAppBar.jsx";
import VideoPlayer from "./components/VideoPlayer.jsx";
import TagSelector from "./components/TagSelector.jsx";
import { Container, Typography } from "@mui/material";

import "./App.css";

const BACKEND_URL = "http://localhost:8000";

const App = () => {
  const [tags, setTags] = useState([]);

  useEffect(() => {
    fetch(`${BACKEND_URL}/tags`)
      .then((response) => response.json())
      .then((data) => {
        setTags(data);
      });
  }, []);

  return (
    <div className="maindiv">
      <div className="search">
        <SearchAppBar />
      </div>
      <div className="tagselector" style={{ margin: "5px" }}>
        <TagSelector tags={tags} />
      </div>
      <div className="videoplayer">
        <VideoPlayer />,
      </div>
    </div>
  );
};

export default App;
