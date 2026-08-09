import { Box, Typography, Link, List, ListItem, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

const SECTIONS = [
  {
    title: 'What Realiti is',
    body: 'Realiti is a place to share what actually happened when you worked with a realtor, and to read what happened to everyone else. Listings and agent profiles already live on a dozen sites. What is missing is the part people only tell their friends: who returned calls, who pushed a bad deal, who went out of their way, and who quietly cost someone thousands.',
    items: [],
  },
  {
    title: 'Back up what you say',
    body: 'You can attach a document or photo to a post as supporting proof. An account backed by something you can point at is worth more than one that is not, and posts without it may carry a warning label.',
    items: [],
  },
  {
    title: 'Every post is screened before it publishes',
    body: 'Posts pass through three checks before anyone else sees them:',
    items: [
      'A text screen for profanity, slurs, and attempts to disguise them',
      'An image screen for explicit or graphic content',
      'A review of the writing itself, and of whether an attached image matches what the post claims',
    ],
  },
  {
    title: 'When something is unclear, a person looks at it',
    body: 'Posts that are obviously fine publish immediately and posts that clearly break the guidelines are blocked outright. Anything in between is held for a human to approve or remove, rather than guessed at. You can also report a post you believe is false or unfair, and attach your own evidence when you do.',
    items: [],
  },
  {
    title: 'What this is not',
    body: 'Realiti is not a place to settle scores. Posts that target someone personally, invent details, or exist to harass rather than inform do not belong here and will be removed. The value of the site depends entirely on accounts being true, so accuracy matters more than intensity.',
    items: [],
  },
  {
    title: 'Coming soon',
    body: 'Realiti is in open testing, and the pieces that make an account stick to the person it describes are still being built:',
    items: [
      'Tagging a post to a named realtor and the state they work in, so accounts collect in one place instead of disappearing into a feed',
      'Realtor profiles, and a way for realtors to claim their own and respond to what is written about them',
      'Verification badges on posts whose supporting proof has been checked',
    ],
  },
  {
    title: 'Expect rough edges',
    body: 'Things will change, break, and get rebuilt while testing continues. If something looks wrong, it may well be. Feedback is worth more to me right now than politeness, so please get in touch.',
    items: [],
  },
];

export default function About(props) {
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 720, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          About Realiti
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Draft, this page describes where Realiti is headed and may change.
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
        <Link component={RouterLink} to="/guidelines" variant="body1">
          Community guidelines
        </Link>
        <Typography component="span" color="text.secondary" sx={{ mx: 1 }}>
          ·
        </Typography>
        <Link component={RouterLink} to="/contact" variant="body1">
          Contact
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
