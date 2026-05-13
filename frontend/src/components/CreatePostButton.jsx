import Button from '@mui/material/Button';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import Dialog from '@mui/material/Dialog';
import { useState } from 'react';
import Post from '../pages/Post.jsx';

const CreatePostButton = () => {
  const [open, setOpen] = useState(false);
  const handleClose = () => {
    setOpen(false);
  };
  return (
    <>
      <Button variant="outlined" endIcon=<AddOutlinedIcon /> onClick={() => setOpen(true)}>
        What's on your mind
      </Button>
      <Dialog onClose={handleClose} open={open} sx={{}}>
        <Post closeProp={handleClose} />
      </Dialog>
    </>
  );
};
export default CreatePostButton;
