import React from 'react';
import SearchAppBar from './components/SearchAppBar.jsx';
import VideoPlayer from './components/VideoPlayer.jsx';
import TagSelector from './components/TagSelector.jsx';
import { Container, Typography } from '@mui/material';


const App = () => {
  
  const tags = ['React', 'JavaScript', 'CSS', 'HTML', 'Node.js', 'Express', 'MongoDB'];
  return (
    
    <div>
      <div>
     <SearchAppBar />
     <VideoPlayer />
     </div>
  
    <div>
    <Typography variant="h4" component="h1" gutterBottom>
      Tag Selector
    </Typography>
    <TagSelector tags={tags} />
    </div>
    </div>
    
  );

};

export default App;
