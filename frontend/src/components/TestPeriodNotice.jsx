import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Link from '@mui/material/Link';
import { Link as RouterLink } from 'react-router-dom';

const TestPeriodNotice = () => (
  <Alert severity="info" sx={{ width: '100%' }}>
    <AlertTitle>Open test:</AlertTitle>
    Realiti is still being built. Accounts, posts, replies, and uploaded images are subject to
    deletion at any time and without notice, so please don&apos;t post anything you&apos;d mind
    losing. Features may change or break while testing continues. See the{' '}
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
