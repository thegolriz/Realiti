import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Stack, Typography, CircularProgress } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import AppTheme from '../shared-theme/AppTheme';
import ColorModeIconDropdown from '../shared-theme/ColorModeIconDropdown';
import NavBar from '../components/NavBar.jsx';
import PostCard from '../components/PostCard.jsx';
import api from '../api/api.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function Profile(props) {
  const { userId } = useParams();
  const { bootstrapping, token, userId: currentUserId } = useAuth();
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState([]);

  // "me" is the nav-drawer link; the numeric branch covers clicking your own
  // avatar on one of your posts, which lands on /profile/<your id>.
  const isSelf = userId === 'me' || (currentUserId != null && userId === String(currentUserId));

  useEffect(() => {
    // Wait for the on-load refresh before fetching so auth state is settled.
    if (bootstrapping) {
      return;
    }
    const fetchData = async () => {
      setLoading(true);
      try {
        const { data: response } = await api.get('/post', { params: { userId } });
        setPosts(response);
      } catch (error) {
        console.error(error.message);
      }
      setLoading(false);
    };
    fetchData();
  }, [bootstrapping, token, userId]);

  // No user endpoint yet, so the name rides along on the posts.
  const displayName = posts[0]?.name;

  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <NavBar />
      <Box
        sx={{
          width: { xs: '100%', md: '50%' },
          margin: '0 auto',
          px: { xs: 2, md: 0 },
          pt: 9,
          pb: 6,
        }}
      >
        <Stack
          direction="row"
          sx={{ alignItems: 'center', justifyContent: 'space-between', mb: 2 }}
        >
          <Typography variant="h4" component="h1">
            {displayName ?? 'Profile'}
          </Typography>
          {isSelf && <ColorModeIconDropdown />}
        </Stack>
        <Stack spacing={1} direction="column" sx={{ alignItems: 'center' }}>
          {loading ? (
            <CircularProgress sx={{ mt: 4 }} />
          ) : posts.length === 0 ? (
            <Typography color="text.secondary" sx={{ mt: 4 }}>
              No posts yet.
            </Typography>
          ) : (
            posts.map(data => (
              <PostCard
                postTitle={data.title}
                key={data.id}
                postId={data.id}
                userId={data.userId}
                userName={data.name}
                postBody={data.description}
                likeCount={data.likes}
                liked={data.liked}
                dislikeCount={data.dislikes}
                disliked={data.disliked}
              />
            ))
          )}
        </Stack>
      </Box>
    </AppTheme>
  );
}
