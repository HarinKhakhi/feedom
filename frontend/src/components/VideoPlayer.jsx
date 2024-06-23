import React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

const VideoPlayer = ({ title, videoUrl }) => {
    return (
        <Card sx={{ maxWidth: 800, margin: 'auto', mt: 5 }}>
            <CardMedia
                component="video"
                controls
                src={videoUrl}
                title={title}
                sx={{ height: 450 }}
            />
            <CardContent>
                <Typography variant="h5" component="div">
                    {title}
                </Typography>
            </CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <Button variant="contained" color="primary">
                    Previous
                </Button>
                <Button variant="contained" color="primary">
                    Next
                </Button>
            </Box>
        </Card>
    );
};

export default VideoPlayer;
