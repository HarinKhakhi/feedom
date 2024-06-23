import React, { useState } from 'react';
import { Box, Chip } from '@mui/material';

const TagSelector = ({ tags }) => {
  const [selectedTags, setSelectedTags] = useState([]);

  const handleToggle = (tag) => {
    setSelectedTags((prevSelectedTags) => {
      if (prevSelectedTags.includes(tag)) {
        return prevSelectedTags.filter((t) => t !== tag);
      } else {
        return [...prevSelectedTags, tag];
      }
    });
  };

  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
      {tags.map((tag) => (
        <Chip
          key={tag}
          label={tag}
          clickable
          color={selectedTags.includes(tag) ? 'primary' : 'default'}
          onClick={() => handleToggle(tag)}
        />
      ))}
    </Box>
  );
};

export default TagSelector;
