import NavBar from '../components/NavBar.jsx';
import { Box, Stack, CircularProgress } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import PostCard from '../components/PostCard.jsx';
import { useState, useEffect } from 'react';
import api from '../api/api.js';
import { useAuth } from '../context/AuthContext.jsx';
import CreatePostButton from '../components/CreatePostButton.jsx';
import TestPeriodNotice from '../components/TestPeriodNotice.jsx';
import AppTheme from '../shared-theme/AppTheme';

const Dashboard = props => {
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState([]);
  const { bootstrapping, token } = useAuth();
  useEffect(() => {
    // Wait for the on-load refresh before fetching so auth state is settled.
    if (bootstrapping) {
      return;
    }
    const fetchData = async () => {
      setLoading(true);
      try {
        const { data: response } = await api.get('/post');
        setPosts(response);
      } catch (error) {
        console.error(error.message);
      }
      setLoading(false);
    };
    fetchData();
  }, [bootstrapping, token]);
  const listPosts = posts.map(data => (
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
  ));
  return (
    <AppTheme {...props}>
      <CssBaseline enableColorScheme />
      <Box>
        <NavBar />
        <Box
          sx={{
            width: { xs: '100%', md: '50%' },
            margin: '0 auto',
            px: { xs: 2, md: 0 },
          }}
        >
          <Stack spacing={1} direction="column" sx={{ mt: 9, alignItems: 'center' }}>
            <CreatePostButton />
            <TestPeriodNotice />
            {loading ? <CircularProgress sx={{ mt: 4 }} /> : listPosts}
          </Stack>
        </Box>
      </Box>
    </AppTheme>
  );
};
export default Dashboard;
