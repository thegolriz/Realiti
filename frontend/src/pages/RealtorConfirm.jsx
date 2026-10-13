import { Box, Typography, Link, Card, Stack, Alert, CircularProgress } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import useSearchParams from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';
import { useEffect } from 'react';

export default function RealtorConfirm(props) {
  // TODO: replace with state driven by confirmRealtor(token).
  // status: 'loading' | 'success' | 'error'
  const status = 'loading';
  const message = '';
  const [params] = useSearchParams();
  const token = params.get('token');

  useEffect(() => {
    if (token === null) {
      return;
    }
  });

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 560, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Card variant="outlined" sx={{ p: { xs: 3, sm: 4 } }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Email confirmation
          </Typography>

          {status === 'loading' && (
            <Stack direction="row" spacing={2} sx={{ alignItems: 'center', py: 2 }}>
              <CircularProgress size={24} />
              <Typography color="text.secondary">Confirming your email...</Typography>
            </Stack>
          )}

          {status === 'success' && (
            <Stack spacing={2}>
              <Alert severity="success">{message}</Alert>
              <Typography variant="h6" component="h2">
                What happens next
              </Typography>
              <Typography variant="body2" color="text.secondary">
                We check your license number against your state's licensing records, and that the
                name on your application matches. This usually takes 1 to 3 days, sometimes longer.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Once you're approved, a "Real estate agent" label appears on your posts and profile.
                You don't need to do anything else.
              </Typography>
            </Stack>
          )}

          {status === 'error' && (
            <Stack spacing={2}>
              <Alert severity="error">{message}</Alert>
              <Typography variant="body2" color="text.secondary">
                Need a new link or more help? Contact{' '}
                <Link href="mailto:support@realiti.dev">support@realiti.dev</Link>.
              </Typography>
            </Stack>
          )}
        </Card>

        <Link component={RouterLink} to="/" variant="body1" sx={{ display: 'inline-block', mt: 3 }}>
          Back to home
        </Link>
      </Box>
    </AppTheme>
  );
}
