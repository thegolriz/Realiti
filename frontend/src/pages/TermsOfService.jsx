import { Box, Typography, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useEffect, useState } from 'react';
import TOS from '../legal/terms-of-service.md';

export default function TermsOfService(props) {
  const [terms, setTerms] = useState(null);
  useEffect(() => {
    fetch(TOS)
      .then(response => response.text())
      .then(text => {
        setTerms(text);
      });
  }, []);
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom></Typography>
        <Markdown remarkPlugins={[remarkGfm]}>{terms}</Markdown>

        <Link component={RouterLink} to="/" variant="body1">
          Back to home
        </Link>
      </Box>
    </AppTheme>
  );
}
