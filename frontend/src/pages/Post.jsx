import { TextField, Box, Input } from '@mui/material';
import PostButton from '../components/PostButton.jsx';

export default function Post() {
  return (
    <Box sx={{
      display: 'flex',
      alignItems: 'center',
      flexDirection: 'column',
      height: '100vh',
      justifyContent: 'center',
      gap: 4,
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
      <Box><PostButton
        text="Post"
        to="/Dashboard" /></Box>
    </Box>
  );
};
