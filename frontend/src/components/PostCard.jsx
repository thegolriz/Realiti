import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Avatar, Stack } from '@mui/material';
import LikeButton from './LikeButton';
import DislikeButton from './DislikeButton';
import ReplyButton from './ReplyButton';
import ReportButton from './ReportButton';
import ReplyCard from './ReplyCard';
import { getReplies } from '../api/api';

const PostCard = ({
  postTitle,
  profilePic,
  userName,
  postBody,
  postId,
  likeCount,
  liked,
  dislikeCount,
  disliked,
}) => {
  const [replies, setReplies] = useState([]);

  const fetchReplies = useCallback(() => {
    getReplies(postId)
      .then(res => setReplies(res.data))
      .catch(err => console.error(err));
  }, [postId]);

  useEffect(() => {
    fetchReplies();
  }, [fetchReplies]);

  return (
    <Box sx={{ minWidth: '100%' }}>
      <Box
        sx={{
          border: 2,
          borderColor: 'rgb(208, 208, 208)',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          p: 2,
          position: 'relative',
        }}
      >
        <Box sx={{ position: 'absolute', top: 8, right: 8 }}>
          <ReportButton postId={postId} />
        </Box>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {postTitle ?? 'Post title'}
        </Typography>
        <Stack spacing={1} direction="row">
          <Avatar alt={userName ?? 'No user attached'} />
          <Box>
            <Typography>{userName ?? 'username'}</Typography>
            <Typography>{postBody}</Typography>
          </Box>
        </Stack>
        <Box
          sx={{
            mt: 1,
            alignSelf: 'flex-start',
            display: 'flex',
            gap: 1,
            alignItems: 'center',
          }}
        >
          <LikeButton postId={postId} initialCount={likeCount} initialLiked={liked} />
          <DislikeButton postId={postId} initialCount={dislikeCount} initialDisliked={disliked} />
          <ReplyButton postId={postId} onReplySubmitted={fetchReplies} />
        </Box>
      </Box>
      {replies.map(reply => (
        <ReplyCard key={reply.id} userName={reply.userName} replyText={reply.reply_text} />
      ))}
    </Box>
  );
};

export default PostCard;
