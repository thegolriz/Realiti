import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Link from '@mui/material/Link';
import { Link as RouterLink } from 'react-router-dom';

// Update these for each round of testing. They are build-time constants, so
// changing them means rebuilding and redeploying the frontend.
const TEST_START = 'August 9, 2026';
const TEST_END = 'August 17, 2026';

const TestPeriodNotice = () => (
  <Alert severity="info" sx={{ width: '100%' }}>
    <AlertTitle>
      Open test: {TEST_START} through {TEST_END}
    </AlertTitle>
    Realiti is still being built. Accounts, posts, replies, and uploaded images
    are subject to deletion at any time and without notice, so please don&apos;t
    post anything you&apos;d mind losing. Features may change or break while
    testing continues. See the{' '}
    <Link component={RouterLink} to="/guidelines">
      guidelines
    </Link>{' '}
    for what belongs here, and{' '}
    <Link component={RouterLink} to="/about">
      learn what Realiti is about
    </Link>
    .
  </Alert>
);

export default TestPeriodNotice;
