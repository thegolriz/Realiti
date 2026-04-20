import { Box, Typography, Avatar, Stack } from '@mui/material';

const PostCard = props => {
  const { postTitle, profilePic, userName, postBody } = props;
  const longText = `Here is a generic post body which will be reaplced with user genereated text\n
                  One could assume that the text body has latin like other text bodies but \n
                  I have opted to do this instead.`;
  return (
    <>
      <Box
        sx={{
          border: 2,
          borderColor: 'rgb(208,	208,	208)',
          borderRadius: 2,
          minHeight: 200,
          minWidth: '100%',
          maxHeight: 400,
          p: 2,
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {postTitle ?? 'Post title'}
        </Typography>
        <Stack spacing={1} direction="row">
          <Avatar alt={userName ?? 'No user attached'}></Avatar>
          <Box>
            <Typography>{userName ?? 'username'}</Typography>
            <Typography>{postBody ?? longText}</Typography>
          </Box>
        </Stack>
      </Box>
    </>
  );
};

export default PostCard;
