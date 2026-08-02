import { useState } from 'react';
import ReplyIcon from '@mui/icons-material/Reply';
import { IconButton, Dialog, Box, TextField, Button } from '@mui/material';
import { postReply } from '../api/api';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from './Notification.jsx';

const ReplyButton = ({ postId, onReplySubmitted }) => {
  const [open, setOpen] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [error, setError] = useState('');
  const { notification, notify, closeNotification } = useNotification();

  const handleClose = () => {
    setOpen(false);
    setReplyText('');
    setError('');
  };

  const handleSubmit = () => {
    if (!replyText.trim()) {
      setError('Reply cannot be empty');
      notify('Reply cannot be empty.', 'warning');
      return;
    }
    postReply({ postId, reply_text: replyText })
      .then(() => {
        handleClose();
        onReplySubmitted?.();
      })
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
      });
  };

  return (
    <>
      <IconButton onClick={() => setOpen(true)}>
        <ReplyIcon />
      </IconButton>
      <Dialog open={open} onClose={handleClose}>
        <Box sx={{ p: 3, display: 'flex', flexDirection: 'column', gap: 2, minWidth: 350 }}>
          <TextField
            label="Write a reply"
            multiline
            rows={3}
            value={replyText}
            onChange={e => setReplyText(e.target.value)}
            error={!!error}
            helperText={error}
            fullWidth
            autoFocus
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={handleClose}>Cancel</Button>
            <Button variant="contained" onClick={handleSubmit}>
              Reply
            </Button>
          </Box>
        </Box>
      </Dialog>
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </>
  );
};

export default ReplyButton;
