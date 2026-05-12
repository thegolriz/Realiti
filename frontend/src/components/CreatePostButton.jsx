import Button from '@mui/material/Button';
import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import PropTypes from 'prop-types';
import Avatar from '@mui/material/Avatar';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import PersonIcon from '@mui/icons-material/Person';
import AddIcon from '@mui/icons-material/Add';
import Typography from '@mui/material/Typography';
import { blue } from '@mui/material/colors';
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
