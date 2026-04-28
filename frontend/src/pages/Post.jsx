import { TextField, Box, Button, FormHelperText } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import * as React from 'react';
import PostButton from '../components/PostButton.jsx';
import { createPost, upload } from '../api/api.js';
import axios from 'axios';


const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});


export default function Post(props) {
  const { closeProp } = props;
  const [descriptionError, setDescriptionError] = React.useState(false);
  const [descriptionErrorMessage, setDescriptionErrorMessage] = React.useState('');
  const [fileHolder, setFileHolder] = React.useState();

  const validateInputs = () => {
    const description = document.getElementById('description');
    if (!description.value || description.value.length < 1) {
      setDescriptionError(true);
      setDescriptionErrorMessage('Please enter an accurate description about your experience');
      return false;
    }
    setDescriptionError(false);
    setDescriptionErrorMessage('');
    return true;
  };

  const handleSubmit = async event => {
    event.preventDefault();
    if (!validateInputs()) {
      return;
    }
    const description = event.currentTarget.description.value;
    const token = localStorage.getItem('token');
    try {
      let documentUrl = null;
      if (fileHolder) {
        const response = await upload({ filename: fileHolder.name }, token);
        const presignedUrl = response.data.s3_url;
        documentUrl = presignedUrl.split('?')[0];
        await axios.put(presignedUrl, fileHolder);
      }
      await createPost({ description, document: documentUrl }, token);
      closeProp && closeProp();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Box
      onSubmit={handleSubmit}
      component="form"
      sx={{
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'column',
        height: '60vh',
        justifyContent: 'center',
        gap: 4,
      }}
    >
      <Box>
        <TextField
          name="description"
          id="description"
          label="Describe your experience"
          fullWidth
          multiline
          variant="outlined"
          error={descriptionError}
          helperText={descriptionErrorMessage}
          sx={{ width: '25vw' }}
        />
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Button
            component="label"
            role={undefined}
            variant="contained"
            tabIndex={-1}
            startIcon={<CloudUploadIcon />}
          >
            Upload files
            <VisuallyHiddenInput
              type="file"
              name="document"
              id="document"
              onChange={event => {
                setFileHolder(event.target.files[0]);
              }}
            />
          </Button>
          {fileHolder && (
            <Box sx={{ fontSize: 13, color: 'text.secondary' }}>{fileHolder.name}</Box>
          )}
        </Box>
        <FormHelperText
          sx={{
            color: 'orange',
            fontWeight: 500,
            fontSize: 14,
            mt: 0.5,
          }}
        >
          A document/image to show proof of your post will go a long way.
          <br /> Without one your post will have a warning label attached. Learn More
        </FormHelperText>
      </Box>
      <Box>
        <PostButton text="Post" />
      </Box>
    </Box>
  );
}
