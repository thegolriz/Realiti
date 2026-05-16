import IconButton from '@mui/material/IconButton';
import BungalowIcon from '@mui/icons-material/Bungalow';
import axios from 'axios';


const handleLike = () => {
  likeSubmit(
    { postId: postId },
    localStorage.getItem('token'),
  )
    .catch(err => {
      console.log(err)
    });
  )};

const LikeButton = props => {
  const { sx, postId } = props
  return (
    <IconButton sx={{ ...sx }}>
      <BungalowIcon />
    </IconButton>
  )
}

export default LikeButton;
