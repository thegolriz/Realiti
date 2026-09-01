import { Box, Typography, Link, List, ListItem, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

const SECTIONS = [
  {
    title: 'Keep up with the newest changes with Realiti',
    body: 'Here you can find every new update that has been added to Realiti!.',
    items: [],
  },
  {
    title: 'Update 08/31/2026',
    body: 'Password changes',
    items: [
      'Passwords now require lenght of 15 or more',
      'Passwords upon creation checks a comprimised database to ensure safety of users',
    ],
  },
];

export default function ReleaseNotes(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Release Notes
        </Typography>

        {SECTIONS.map(section => (
          <Box key={section.title} sx={{ mb: 3 }}>
            <Typography variant="h5" component="h2" gutterBottom>
              {section.title}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {section.body}
            </Typography>
            {section.items.length > 0 && (
              <List sx={{ listStyleType: 'disc', pl: 4, py: 0 }}>
                {section.items.map(item => (
                  <ListItem key={item} sx={{ display: 'list-item', px: 0, py: 0.25 }}>
                    <Typography variant="body1" color="text.secondary">
                      {item}
                    </Typography>
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        ))}

        <Divider sx={{ my: 3 }} />
        <Link component={RouterLink} to="/" variant="body1">
          Back to home
        </Link>
      </Box>
    </AppTheme>
  );
}
