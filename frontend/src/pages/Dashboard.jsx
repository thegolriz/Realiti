import NavBar from '../components/NavBar.jsx';
import { Box, Stack, CircularProgress } from '@mui/material';
import PostCard from '../components/PostCard.jsx';
import { useState, useEffect } from 'react';
import api from '../api/api.js';
import CreatePostButton from '../components/CreatePostButton.jsx';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [posts, setPosts] = useState([]);
  useEffect(() => {
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
  }, []);
  console.log('Posts here\n', posts);
  const listPosts = posts.map(data => (
    <PostCard
      postTitle={data.title}
      key={data.id}
      postId={data.id}
      userName={data.name}
      postBody={data.description}
      likeCount={data.likes}
      liked={data.liked}
      dislikeCount={data.dislikes}
      disliked={data.disliked}
    />
  ));
  return (
    <Box>
      <NavBar />
      <Box sx={{ width: '50%', margin: '0 auto' }}>
        <Stack spacing={1} direction="column" sx={{ mt: 9, alignItems: 'center' }}>
          <CreatePostButton />
          {loading ? <CircularProgress sx={{ mt: 4 }} /> : listPosts}
        </Stack>
      </Box>
    </Box>
  );
};
export default Dashboard;
