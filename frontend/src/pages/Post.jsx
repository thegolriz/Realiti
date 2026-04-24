import { TextField, Box, Button, Input, FormControl, FormHelperText } from '@mui/material';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import * as React from 'react';
import PostButton from '../components/PostButton.jsx';
import { createPost, upload } from '../api/api.js';
import axios from 'axios';

export default function Post(props) {
  const { closeProp } = props;
  const [descriptionError, setDescriptionError] = React.useState(false);
  const [descriptionErrorMessage, setDescriptionErrorMessage] = React.useState('');
  const [documentError, setDocumentError] = React.useState(false);
  const [documentErrorMessage, setDocumentErrorMessage] = React.useState('');
  const [uploadedFileNames, setUploadedFileNames] = React.useState([]);

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

  const validateInputs = () => {
    const description = document.getElementById('description');
    const documents = document.getElementById('document');
    let isValid = true;
    if (!description.value || description.value.length < 1) {
      setDescriptionError(true);
      setDescriptionErrorMessage('Please enter an accurate description about your experience');
      isValid = false;
    } else {
      setDescriptionError(false);
      setDescriptionErrorMessage('');
    }
    if (!documents.value) {
      setDocumentError(true);
      setDocumentErrorMessage('Please provide an image or supporting document for your post');
      isValid = false;
    } else {
      setDocumentError(false);
      setDocumentErrorMessage('');
    }
    return isValid;
  };

  const handleSubmit = event => {
    event.preventDefault();
    if (!validateInputs()) {
      return;
    }
    const data = new FormData(event.currentTarget);
    upload({ filename: data.get('document').name }, localStorage.getItem('token'))
      .then(response => {
        const presignedUrl = response.data.s3_url;
        const cleanUrl = presignedUrl.split('?')[0];
        return axios
          .put(presignedUrl, data.get('document'))
          .then(() =>
            createPost(
              { description: data.get('description'), document: cleanUrl },
              localStorage.getItem('token')
            )
          )
          .then(() => closeProp());
      })
      .catch(err => {
        console.error(err);
      });
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
                const files = Array.from(event.target.files);
                setUploadedFileNames(files.map(f => f.name));
              }}
              multiple
            />
          </Button>
          {uploadedFileNames.length > 0 && (
            <Box sx={{ fontSize: 13, color: 'text.secondary' }}>{uploadedFileNames.join(', ')}</Box>
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
