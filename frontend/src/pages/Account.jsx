import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Stack,
  Divider,
  FormControl,
  FormLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { useNavigate } from 'react-router-dom';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from '../components/Notification.jsx';
import { getAccount, changePassword, deleteAccount } from '../api/api';
import { useAuth } from '../context/AuthContext.jsx';

export default function Account(props) {
  const navigate = useNavigate();
  const { logout, bootstrapping } = useAuth();
  const { notification, notify, closeNotification } = useNotification();

  const [account, setAccount] = useState(null);

  const [current, setCurrent] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirm, setConfirm] = useState('');

  const [deletePassword, setDeletePassword] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);

  // Wait for the on-load refresh so the access token is set before we fetch.
  useEffect(() => {
    if (bootstrapping) {
      return;
    }
    getAccount()
      .then(res => setAccount(res.data))
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bootstrapping]);

  const handlePasswordChange = e => {
    e.preventDefault();
    if (!current || !newPass || !confirm) {
      notify('All password fields are required.', 'warning');
      return;
    }
    if (newPass !== confirm) {
      notify('New passwords do not match.', 'warning');
      return;
    }
    changePassword({
      current_password: current,
      new_password: newPass,
      confirm_password: confirm,
    })
      .then(() => {
        notify('Password updated.', 'success');
        setCurrent('');
        setNewPass('');
        setConfirm('');
      })
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
      });
  };

  const handleDelete = () => {
    setConfirmOpen(false);
    deleteAccount(deletePassword)
      .then(async () => {
        // Leave the protected account page before auth clears, so we land on
        // the public dashboard instead of being redirected to signin.
        navigate('/');
        await logout();
      })
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
      });
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 560, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
          Account
        </Typography>

        <Stack spacing={0.5} sx={{ mb: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Name
          </Typography>
          <Typography sx={{ mb: 1 }}>{account ? account.first_name : 'Loading...'}</Typography>
          <Typography variant="body2" color="text.secondary">
            Email
          </Typography>
          <Typography>{account ? account.email : 'Loading...'}</Typography>
        </Stack>

        <Divider sx={{ mb: 3 }} />

        <Typography variant="h6" sx={{ mb: 2 }}>
          Change password
        </Typography>
        <Box component="form" onSubmit={handlePasswordChange}>
          <Stack spacing={2}>
            <FormControl>
              <FormLabel htmlFor="current-password">Current password</FormLabel>
              <TextField
                type="password"
                id="current-password"
                value={current}
                onChange={e => setCurrent(e.target.value)}
                fullWidth
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="new-password">New password</FormLabel>
              <TextField
                type="password"
                id="new-password"
                value={newPass}
                onChange={e => setNewPass(e.target.value)}
                helperText="At least 8 characters"
                fullWidth
              />
            </FormControl>
            <FormControl>
              <FormLabel htmlFor="confirm-password">Confirm new password</FormLabel>
              <TextField
                type="password"
                id="confirm-password"
                value={confirm}
                onChange={e => setConfirm(e.target.value)}
                fullWidth
              />
            </FormControl>
            <Button type="submit" variant="contained" sx={{ alignSelf: 'flex-start' }}>
              Update password
            </Button>
          </Stack>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Typography variant="h6" color="error" sx={{ mb: 1 }}>
          Delete account
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          This permanently removes your account and everything attached to it: your posts, replies,
          likes, and dislikes. It cannot be undone.
        </Typography>
        <Stack spacing={2}>
          <FormControl>
            <FormLabel htmlFor="delete-password">Password</FormLabel>
            <TextField
              type="password"
              id="delete-password"
              value={deletePassword}
              onChange={e => setDeletePassword(e.target.value)}
              fullWidth
            />
          </FormControl>
          <Button
            variant="contained"
            color="error"
            sx={{ alignSelf: 'flex-start' }}
            onClick={() => {
              if (!deletePassword) {
                notify('Enter your password to confirm.', 'warning');
                return;
              }
              setConfirmOpen(true);
            }}
          >
            Delete account
          </Button>
        </Stack>
      </Box>

      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)}>
        <DialogTitle>Delete your account?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This is permanent and removes all of your posts, replies, likes, and dislikes. There is
            no way to recover it.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete}>
            Delete forever
          </Button>
        </DialogActions>
      </Dialog>

      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </AppTheme>
  );
}
