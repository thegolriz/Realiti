import { Typography, IconButton, Box } from '@mui/material';
import BungalowIcon from '@mui/icons-material/Bungalow';
import { postLike } from '../api/api';
import { useState } from 'react';

const LikeButton = props => {
  const { sx, postId } = props;
  const [likes, setLikes] = useState(0);
  const [liked, setLiked] = useState(false);

  const handleLike = () => {
    postLike({ postId: postId }, localStorage.getItem('token'))
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
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Typography>{likes > 0 ? likes : ''}</Typography>
      <IconButton sx={{ ...sx }} onClick={handleLike}>
        <BungalowIcon sx={{ color: liked ? 'orange' : 'inherit' }} />
      </IconButton>
    </Box>
  );
};

export default LikeButton;
