import { Typography, IconButton, Box } from '@mui/material';
import BungalowIcon from '@mui/icons-material/Bungalow';
import { postLike } from '../api/api';
import { useState } from 'react';

const LikeButton = props => {
  const { sx, postId, initialCount = 0, initialLiked = false } = props;
  const [likes, setLikes] = useState(initialCount);
  const [liked, setLiked] = useState(initialLiked);

  const handleLike = () => {
    postLike({ postId: postId })
      .then(res => {
        if (res.data.liked) {
          setLikes(prev => prev + 1);
          setLiked(true);
        } else {
          setLikes(prev => prev - 1);
          setLiked(false);
        }
      })
      .catch(err => {
        console.log(err);
      });
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Typography>{likes > 0 ? likes : ''}</Typography>
      <IconButton sx={{ ...sx }} onClick={handleLike}>
        <BungalowIcon sx={{ color: liked ? 'orange' : 'inherit' }} />
      </IconButton>
    </Box>
  );
};

export default LikeButton;
