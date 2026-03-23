import { TextField, Box, Input } from '@mui/material';

export default function Post() {
  return (
    <Box sx={{
      display: 'flex',
      alignItems: 'center',
      flexDirection: 'column',
      height: '100vh',
      justifyContent: 'center',
    }}>
      <Box>
        <TextField id="outlined-basic" label="Describe your expierence" fullWidth multiline variant="outlined" sx={{
          width: '50vw',
        }} />
      </Box>
      <Box>
        <Input type='file'>
          Upload an image/file to support your post
        </Input>
      </Box>
      <Box>Post button here</Box>
    </Box>
  );
};
