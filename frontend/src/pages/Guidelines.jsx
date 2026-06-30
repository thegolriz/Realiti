import { Box, Typography, Link, List, ListItem, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

const SECTIONS = [
  {
    title: 'Be authentic',
    body: 'Share real experiences in your own words. Posts that disguise their content — leetspeak, spaced-out letters, or other attempts to slip past our filters — do not meet our guidelines.',
    items: [],
  },
  {
    title: 'Prohibited content',
    body: 'The following is not allowed and will be removed:',
    items: [
      'Profanity, slurs, or hateful language',
      'Sexually explicit or graphic imagery',
      'Harassment, threats, or content that targets an individual',
      'Spam, scams, or misleading information',
    ],
  },
  {
    title: 'Formatting',
    body: 'Keep posts readable. Avoid obfuscated text, excessive symbols, or character substitutions meant to evade moderation.',
    items: [],
  },
  {
    title: 'Proof & accuracy',
    body: 'Attaching a document or image to back up your experience builds trust. Posts without supporting proof may carry a warning label.',
    items: [],
  },
  {
    title: 'Enforcement',
    body: 'Posts that fail moderation are blocked before they are published. Repeated or severe violations may affect your account. (Details to be finalized.)',
    items: [],
  },
];

export default function Guidelines(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Community Guidelines
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Draft — these guidelines are still being finalized and may change.
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
