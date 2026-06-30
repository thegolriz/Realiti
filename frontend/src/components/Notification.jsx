import * as React from 'react';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

// Reusable popup for surfacing errors / warnings.
// severity="error" -> red box, severity="warning" -> yellow box.
// The Alert renders a dismiss "x" automatically when onClose is provided.
export default function Notification({ open, message, severity = 'error', onClose }) {
  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={(_event, reason) => {
        if (reason === 'clickaway') {
          return;
        }
        onClose();
      }}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert onClose={onClose} severity={severity} variant="filled" sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
}

// Small hook so each page can fire popups without repeating boilerplate.
export function useNotification() {
  const [notification, setNotification] = React.useState({
    open: false,
    message: '',
    severity: 'error',
  });

  const notify = (message, severity = 'error') => {
    setNotification({ open: true, message, severity });
  };

  const closeNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return { notification, notify, closeNotification };
}

// Pull the human-readable error out of an axios error.
export function getServerError(err) {
  return err?.response?.data?.error || 'Something went wrong. Please try again.';
}

// Decide whether a server error should show as a red error or a yellow warning.
// Recoverable input problems (too short, already taken, missing/required) -> warning.
// Everything else (bad credentials, moderation rejection, etc.) -> error.
const WARNING_HINTS = [
  'in use',
  'already',
  'taken',
  'at least',
  'characters',
  'required',
  'valid email',
  'missing',
  'empty',
  'cannot be',
  'guideline',
];

export function serverErrorSeverity(message) {
  const text = (message || '').toLowerCase();
  return WARNING_HINTS.some(hint => text.includes(hint)) ? 'warning' : 'error';
}
