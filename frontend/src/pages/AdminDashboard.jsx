import { useState, useEffect } from 'react';
import { Box, Typography, Button, Stack, Divider, Card, CardContent } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import NavBar from '../components/NavBar.jsx';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from '../components/Notification.jsx';
import { getReviewPosts, approvePost, rejectPost, getReports, resolveReport } from '../api/api';

export default function AdminDashboard(props) {
  const [reviewPosts, setReviewPosts] = useState([]);
  const [reports, setReports] = useState([]);
  const { notification, notify, closeNotification } = useNotification();

  const showError = err => {
    const message = getServerError(err);
    notify(message, serverErrorSeverity(message));
  };

  const load = () => {
    getReviewPosts()
      .then(res => setReviewPosts(res.data))
      .catch(showError);
    getReports()
      .then(res => setReports(res.data))
      .catch(showError);
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runAction = (promise, successMsg) => {
    promise
      .then(() => {
        notify(successMsg, 'success');
        load();
      })
      .catch(showError);
  };

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box sx={{ maxWidth: 800, mx: 'auto', px: 3, pt: 12, pb: 6 }}>
        <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
          Admin dashboard
        </Typography>

        <Typography variant="h6" sx={{ mb: 2 }}>
          Awaiting review ({reviewPosts.length})
        </Typography>
        <Stack spacing={2} sx={{ mb: 4 }}>
          {reviewPosts.length === 0 && (
            <Typography color="text.secondary">Nothing to review.</Typography>
          )}
          {reviewPosts.map(post => (
            <Card key={post.id} variant="outlined">
              <CardContent>
                <Typography sx={{ fontWeight: 600 }}>{post.title || 'Untitled'}</Typography>
                <Typography sx={{ mb: 1 }}>{post.description}</Typography>
                <Typography variant="body2" color="text.secondary">
                  by {post.name}
                </Typography>
                {post.review_reason && (
                  <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
                    Flagged: {post.review_reason}
                  </Typography>
                )}
                <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => runAction(approvePost(post.id), 'Post approved.')}
                  >
                    Approve
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => runAction(rejectPost(post.id), 'Post removed.')}
                  >
                    Reject
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>

        <Divider sx={{ mb: 3 }} />

        <Typography variant="h6" sx={{ mb: 2 }}>
          Reports ({reports.length})
        </Typography>
        <Stack spacing={2}>
          {reports.length === 0 && <Typography color="text.secondary">No open reports.</Typography>}
          {reports.map(report => (
            <Card key={report.id} variant="outlined">
              <CardContent>
                <Typography variant="body2" color="error" sx={{ mb: 1 }}>
                  Reason: {report.reason}
                </Typography>
                {report.post ? (
                  <>
                    <Typography sx={{ fontWeight: 600 }}>
                      {report.post.title || 'Untitled'}
                    </Typography>
                    <Typography sx={{ mb: 1 }}>{report.post.description}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      by {report.post.name}
                    </Typography>
                  </>
                ) : (
                  <Typography color="text.secondary">
                    The reported post no longer exists.
                  </Typography>
                )}
                {report.evidence_url && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Evidence: {report.evidence_url}
                  </Typography>
                )}
                <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    color="error"
                    onClick={() =>
                      runAction(resolveReport(report.id, 'uphold'), 'Report upheld, post removed.')
                    }
                  >
                    Uphold & remove
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() =>
                      runAction(resolveReport(report.id, 'dismiss'), 'Report dismissed.')
                    }
                  >
                    Dismiss
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Stack>
      </Box>
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </AppTheme>
  );
}
