import { Typography, IconButton, Box } from '@mui/material';
import BungalowIcon from '@mui/icons-material/Bungalow';
import { postDislike } from '../api/api';
import { useState } from 'react';

const DislikeButton = props => {
  const { sx, postId } = props;
  const [dislikes, setDislikes] = useState(0);
  const [disliked, setDisliked] = useState(false);

  const handleDislike = () => {
    postDislike({ postId: postId }, localStorage.getItem('token'))
      .then(res => {
        if (res.data.disliked) {
          setDislikes(prev => prev + 1);
          setDisliked(true);
        } else {
          setDislikes(prev => prev - 1);
          setDisliked(false);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Typography>{dislikes > 0 ? dislikes : ''}</Typography>
      <IconButton sx={{ ...sx }} onClick={handleDislike}>
        <BungalowIcon sx={{ color: disliked ? 'red' : 'inherit', transform: 'rotate(180deg)' }} />
      </IconButton>
    </Box>
  );
};

export default DislikeButton;
