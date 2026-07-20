import { Box, Typography } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

export default function Account(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1">
          Account dashboard tbd
        </Typography>
      </Box>
    </AppTheme>
  );
}
