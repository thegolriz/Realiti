import { Box, Typography, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

export default function TermsOfService(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Terms of Service
        </Typography>
        <Link component={RouterLink} to="/" variant="body1">
          Back to home
        </Link>
      </Box>
    </AppTheme>
  );
}
