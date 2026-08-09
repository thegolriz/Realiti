import { Box, Typography, Link, List, ListItem, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

const CONTACT_EMAIL = 'support@realiti.dev';

const USEFUL_DETAILS = [
  'What you were trying to do, and what happened instead',
  'The page you were on, and roughly when',
  'A screenshot, if something looked wrong',
  'The email on your account, if the problem is with your account',
];

export default function Contact(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Contact
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Realiti is in open testing, so questions, bug reports, and blunt
          feedback are all welcome.
        </Typography>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Get in touch
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Questions, bug reports, and anything else can go to{' '}
            <Link href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</Link>. You do
            not need an account to write in. It is one person reading these, so
            replies may take a few days.
          </Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            Problems with a specific post
          </Typography>
          <Typography variant="body1" color="text.secondary">
            If a post is false, unfair, or breaks the{' '}
            <Link component={RouterLink} to="/guidelines">
              guidelines
            </Link>
            , use the report button on the post itself rather than email.
            Reports arrive with the post attached, which makes them much faster
            to act on.
          </Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" gutterBottom>
            What helps when reporting a bug
          </Typography>
          <List sx={{ listStyleType: 'disc', pl: 4, py: 0 }}>
            {USEFUL_DETAILS.map(detail => (
              <ListItem key={detail} sx={{ display: 'list-item', px: 0, py: 0.25 }}>
                <Typography variant="body1" color="text.secondary">
                  {detail}
                </Typography>
              </ListItem>
            ))}
          </List>
        </Box>

        <Divider sx={{ my: 3 }} />
        <Link component={RouterLink} to="/about" variant="body1">
          About Realiti
        </Link>
        <Typography component="span" color="text.secondary" sx={{ mx: 1 }}>
          ·
        </Typography>
        <Link component={RouterLink} to="/" variant="body1">
          Back to home
        </Link>
      </Box>
    </AppTheme>
  );
}
