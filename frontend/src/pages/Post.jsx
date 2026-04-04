import { TextField, Box, Input, FormControl } from '@mui/material';
import * as React from 'react';
import PostButton from '../components/PostButton.jsx';
import { createPost, upload } from '../api/api.js';
import axios from "axios";

export default function Post() {
  const [descriptionError, setDescriptionError] = React.useState(false);
  const [descriptionErrorMessage, setDescriptionErrorMessage] = React.useState('');
  const [documentError, setDocumentError] = React.useState(false);
  const [documentErrorMessage, setDocumentErrorMessage] = React.useState('');

  const validateInputs = () => {
    const description = document.getElementById('description');
    const documents = document.getElementById('document');
    let isValid = true;
    if (!description.value || description.value.length < 1) {
      setDescriptionError(true);
      setDescriptionErrorMessage('Please enter an accurate description about your expierence')
      isValid = false;
    } else {
      setDescriptionError(false);
      setDescriptionErrorMessage('');
    }
    if (!documents.value) {
      setDocumentError(true);
      setDocumentErrorMessage('Please provide an image or supporting document for your post')
    } else {
      setDocumentError(false);
      setDocumentErrorMessage('');
    }
    return isValid;
  }
  const handleSubmit = (event) => {
    event.preventDefault();
    if (descriptionError || documentError) {
      return;
    }
    const data = new FormData(event.currentTarget);
    console.log({
      description: data.get('description'),
      document: data.get('document')
    });
    console.log(localStorage.getItem('token'))
    upload(
      { filename: data.get('document').name, }, localStorage.getItem('token')
    )
      .then((response) => {
        console.log(response.data);
        const presignedUrl = response.data.s3_url;
        const cleanUrl = presignedUrl.split('?')[0];
        return axios.put(presignedUrl, data.get('document'))
          .then(() => {
            return createPost(
              { description: data.get('description'), document: cleanUrl },
              localStorage.getItem('token')
            );
          })
          .then((response) => {
            console.log(response.data);
          });
      })
      .catch((err => {
        console.error(err);
      }));
  };
  return (
    <Box
      onSubmit={handleSubmit}
      component="form"
      sx={{
        display: 'flex',
        alignItems: 'center',
        flexDirection: 'column',
        height: '100vh',
        justifyContent: 'center',
        gap: 4,
      }}>
      <Box>
        <TextField name="description" id="description" label="Describe your expierence" fullWidth multiline variant="outlined" sx={{
          width: '50vw',
        }} />
      </Box>
      <Box>
        <Input name="document" id="document" type='file'>
          Upload an image/file to support your post
        </Input>
      </Box>
      <Box><PostButton
        text="Post"
        onClick={validateInputs}
      /></Box>
    </Box>
  );
};
