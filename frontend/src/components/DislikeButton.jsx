import { Typography, IconButton, Box } from '@mui/material';
import BungalowIcon from '@mui/icons-material/Bungalow';
import { postDislike } from '../api/api';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

const DislikeButton = props => {
  const { sx, postId, initialCount = 0, initialDisliked = false } = props;
  const [dislikes, setDislikes] = useState(initialCount);
  const [disliked, setDisliked] = useState(initialDisliked);
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  const handleDislike = () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    postDislike({ postId: postId })
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
        console.error(err);
      });
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Typography>{dislikes > 0 ? dislikes : ''}</Typography>
      <IconButton sx={{ ...sx }} onClick={handleDislike}>
        <BungalowIcon sx={{ color: disliked ? 'red' : 'inherit', transform: 'rotate(180deg)' }} />
      </IconButton>
    </Box>
  );
};

export default DislikeButton;
