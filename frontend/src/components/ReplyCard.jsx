import { Box, Typography, Avatar, Stack } from '@mui/material';

const ReplyCard = ({ userName, replyText }) => {
  return (
    <Box
      sx={{
        border: 1,
        borderColor: 'rgb(225, 225, 225)',
        borderRadius: 2,
        p: 1.5,
        ml: 4,
        mt: 0.5,
        backgroundColor: 'action.hover',
      }}
    >
      <Stack spacing={1} direction="row" alignItems="flex-start">
        <Avatar sx={{ width: 26, height: 26, fontSize: 13 }} alt={userName} />
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 600, lineHeight: 1.3 }}>
            {userName}
          </Typography>
          <Typography variant="body2">{replyText}</Typography>
        </Box>
      </Stack>
    </Box>
  );
};

export default ReplyCard;
