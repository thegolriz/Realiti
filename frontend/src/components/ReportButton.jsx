import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FlagOutlinedIcon from '@mui/icons-material/FlagOutlined';
import {
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Stack,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import { reportPost } from '../api/api';
import { useAuth } from '../context/AuthContext.jsx';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from './Notification.jsx';

const REPORT_REASONS = [
  'Inappropriate content',
  'Spam or advertising',
  'False or misleading information',
  'Harassment or hate speech',
  'Scam or fraud',
];

export default function ReportButton({ postId }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [evidenceUrl, setEvidenceUrl] = useState('');
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();
  const { notification, notify, closeNotification } = useNotification();

  const handleOpen = () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setReason('');
    setEvidenceUrl('');
  };

  const handleSubmit = () => {
    if (!reason) {
      notify('Please choose a reason for the report.', 'warning');
      return;
    }
    reportPost({ postId, reason, evidence_url: evidenceUrl || undefined })
      .then(() => {
        notify('Report submitted. Thanks for flagging it.', 'success');
        handleClose();
      })
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
      });
  };

  return (
    <>
      <IconButton onClick={handleOpen} aria-label="report post">
        <FlagOutlinedIcon />
      </IconButton>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Report this post</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1, minWidth: 350 }}>
            <FormControl>
              <FormLabel id="report-reason-label">Why are you reporting this?</FormLabel>
              <RadioGroup
                aria-labelledby="report-reason-label"
                value={reason}
                onChange={e => setReason(e.target.value)}
              >
                {REPORT_REASONS.map(option => (
                  <FormControlLabel
                    key={option}
                    value={option}
                    control={<Radio />}
                    label={option}
                  />
                ))}
              </RadioGroup>
            </FormControl>
            <TextField
              placeholder="Link to proof (optional)"
              value={evidenceUrl}
              onChange={e => setEvidenceUrl(e.target.value)}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleSubmit}>
            Submit report
          </Button>
        </DialogActions>
      </Dialog>
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </>
  );
}
