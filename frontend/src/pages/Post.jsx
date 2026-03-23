import { Container, Box } from '@mui/material';

export default function Post() {
  return (
    <Container sx={{
      backgroundColor: 'red',
      display: 'flex',
      alignItems: 'center',
      minHeight: 400,
    }}>
      <Box>Post text here</Box>
      <Box>Post image/document upload here</Box>
      <Box>Post button here</Box>
    </Container>
  );
};
