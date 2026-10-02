import { Box, Typography, Link, List, ListItem, Divider } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';

const SECTIONS = [
  {
    title: 'Be authentic',
    body: 'Share real experiences in your own words. Posts that disguise their content: leetspeak, spaced-out letters, or other attempts to slip past our filters, do not meet our guidelines.',
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
    body: 'Attaching a document or image helps verify your experience. Posts with an image or document will display a verified badge once approved.',
    items: [],
  },
  {
    title: 'Enforcement',
    body: 'Posts that fail moderation are blocked before they are published. Repeated or severe violations may affect your account. (Details to be finalized.)',
    items: [],
  },
  {
    title: 'Held posts',
    body: 'Posts that do not clearly pass or fail automated moderation are held for manual review. This typically takes 24-72 hours, though it may take longer during periods of high traffic. Once reviewed, the post will either go live or be rejected.',
    items: [],
  },
  {
    title: 'Image/Documents for posts',
    body: 'Attaching an image or document for a post helps your post stand out',
    items: [
      'Images and documents do not show up on posts to protect privacy of users',
      'They are reviewd by our moderation pipeline to see if they fit the post you create',
      'Additional investigating may be done for images or documents on a case by case basis',
    ],
  },
  {
    id: 'realtor-specific',
    title: 'Realtor-specific rules',
    body: 'This is not an advertising space. Realtors can share experiences, tips, and invitations to connect, but the following rules apply in addition to everything above:',
    items: [
      'No listings or property-specific advertising: no addresses, prices, square footage, or "I have a listing" posts',
      'Open house invitations are allowed as a social invitation to meet',
      'Inviting people to reach out to you is allowed, for example referencing positive feedback and sharing how to contact you',
      'No naming other users: they haven’t agreed to the same visibility you have as a realtor',
      'No naming other realtors or brokerages, including your own: keeps things professional and avoids reputation disputes',
      'Describe what happened without naming who it was with; the situation is fair game, the name isn’t',
      'Sharing a link or contact info in response to someone’s interest is allowed',
    ],
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
          Draft, these guidelines are still being finalized and may change.
          <br />
          <Link href="#realtor-specific">Realtor specific guidelines here</Link>
        </Typography>

        {SECTIONS.map(section => (
          <Box key={section.title} id={section.id} sx={{ mb: 3 }}>
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
