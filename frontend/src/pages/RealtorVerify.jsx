import {
  Box,
  Typography,
  Link,
  Card,
  Stack,
  FormControl,
  FormLabel,
  TextField,
  MenuItem,
  Button,
  Alert,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';
import { getAccount, applyRealtor } from '../api/api.js';
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from '../components/Notification.jsx';

const US_STATES = (
  'AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO ' +
  'MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY'
).split(' ');

export default function RealtorVerify(props) {
  const { notification, notify, closeNotification } = useNotification();
  const { bootstrapping } = useAuth();
  const [account, setAccount] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  // Set on a successful apply; swaps the form for the "check your email" view.
  const [submitted, setSubmitted] = useState(null);
  const submittingRef = useRef(false);

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

  const validateInputs = data => {
    const values = [
      account?.first_name,
      account?.last_name,
      data.get('license_number'),
      data.get('state'),
      data.get('city'),
    ];
    if (values.some(v => !v || !v.trim())) {
      notify('Please fill in every field.', 'warning');
      return false;
    }
    return true;
  };

  const handleSubmit = event => {
    event.preventDefault();
    // A double tap would send twice before `submitting` re-renders.
    if (submittingRef.current) {
      return;
    }
    const data = new FormData(event.currentTarget);
    if (!validateInputs(data)) {
      return;
    }
    submittingRef.current = true;
    setSubmitting(true);
    applyRealtor({
      first_name: account.first_name,
      last_name: account.last_name,
      email: account.email,
      license_number: data.get('license_number'),
      state: data.get('state'),
      city: data.get('city'),
    })
      .then(res => {
        // The form goes away on success: the application exists, so a second
        // submit would only hit "already applied".
        setSubmitted({ warning: res.data.warning ?? null });
      })
      .catch(err => {
        const message = getServerError(err);
        notify(message, serverErrorSeverity(message));
        submittingRef.current = false;
        setSubmitting(false);
      });
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 560, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Card variant="outlined" sx={{ p: { xs: 3, sm: 4 } }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Real estate agent verification
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Verified agents get a "Real estate agent" label on their posts and profile. We check
            your license against your state's licensing records, which usually takes 1 to 3 days.
          </Typography>

          {submitted ? (
            <Stack spacing={2}>
              {submitted.warning ? (
                // The send failed, so there's no link to open yet.
                <Alert severity="warning">{submitted.warning}</Alert>
              ) : (
                <>
                  <Alert severity="success">
                    We sent a confirmation link to <strong>{account?.email}</strong>.
                  </Alert>
                  <Typography variant="body2" color="text.secondary">
                    Open the link within 24 hours to send your application for review. If you don't
                    see the email, check your spam folder.
                  </Typography>
                </>
              )}
            </Stack>
          ) : (
            <>
              <Alert severity="info" sx={{ mb: 3 }}>
                Enter your name exactly as it appears on your license, or your application will be
                rejected.
              </Alert>

              <Box
                component="form"
                onSubmit={handleSubmit}
                noValidate
                sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
              >
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <FormControl fullWidth>
                    <FormLabel htmlFor="first_name">First name</FormLabel>
                    <TextField
                      id="first_name"
                      name="first_name"
                      onChange={e => setAccount({ ...account, first_name: e.target.value })}
                      value={account?.first_name ?? ''}
                      fullWidth
                    />
                  </FormControl>
                  <FormControl fullWidth>
                    <FormLabel htmlFor="last_name">Last name</FormLabel>
                    <TextField
                      id="last_name"
                      onChange={e => setAccount({ ...account, last_name: e.target.value })}
                      value={account?.last_name ?? ''}
                      name="last_name"
                      fullWidth
                    />
                  </FormControl>
                </Stack>

                <FormControl fullWidth>
                  <FormLabel htmlFor="email">Email</FormLabel>
                  <TextField
                    id="email"
                    name="email"
                    value={account?.email ?? ''}
                    fullWidth
                    helperText="We'll send a confirmation link to the email on your account."
                    slotProps={{ input: { readOnly: true } }}
                  />
                </FormControl>

                <FormControl fullWidth>
                  <FormLabel htmlFor="license_number">License number</FormLabel>
                  <TextField
                    id="license_number"
                    name="license_number"
                    required
                    fullWidth
                    placeholder="e.g. SL3456789"
                    slotProps={{ htmlInput: { maxLength: 30 } }}
                  />
                </FormControl>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <FormControl sx={{ minWidth: { sm: 140 } }}>
                    <FormLabel htmlFor="state">License state</FormLabel>
                    <TextField id="state" name="state" select required defaultValue="">
                      {US_STATES.map(code => (
                        <MenuItem key={code} value={code}>
                          {code}
                        </MenuItem>
                      ))}
                    </TextField>
                  </FormControl>
                  <FormControl fullWidth>
                    <FormLabel htmlFor="city">City</FormLabel>
                    <TextField id="city" name="city" required fullWidth placeholder="Miami" />
                  </FormControl>
                </Stack>

                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={submitting}
                  sx={{ mt: 1 }}
                >
                  {submitting ? 'Submitting...' : 'Submit for verification'}
                </Button>
              </Box>
            </>
          )}
        </Card>

        <Link component={RouterLink} to="/" variant="body1" sx={{ display: 'inline-block', mt: 3 }}>
          Back to home
        </Link>
      </Box>
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </AppTheme>
  );
}
