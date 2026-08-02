import Button from '@mui/material/Button';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import Dialog from '@mui/material/Dialog';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Post from '../pages/Post.jsx';
import { useAuth } from '../context/AuthContext.jsx';

const CreatePostButton = () => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();
  const handleClose = () => {
    setOpen(false);
  };
  const handleOpen = () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    setOpen(true);
  };
  return (
    <>
      <Button variant="outlined" endIcon={<AddOutlinedIcon />} onClick={handleOpen}>
        What's on your mind
      </Button>
      <Dialog onClose={handleClose} open={open} sx={{}}>
        <Post closeProp={handleClose} />
      </Dialog>
    </>
  );
};
export default CreatePostButton;
