import { TextField, Box, Button, FormHelperText, Link, IconButton } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CloseIcon from '@mui/icons-material/Close';
import * as React from 'react';
import PostButton from '../components/PostButton.jsx';
import { createPost, upload } from '../api/api.js';
import axios from 'axios';
import Notification, {
  useNotification,
  getServerError,
  serverErrorSeverity,
} from '../components/Notification.jsx';

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
  const [submitting, setSubmitting] = React.useState(false);
  const fileInputRef = React.useRef(null);
  const submittingRef = React.useRef(false);
  const mountedRef = React.useRef(true);
  const { notification, notify, closeNotification } = useNotification();

  React.useEffect(
    () => () => {
      mountedRef.current = false;
    },
    []
  );

  const handleRemoveFile = () => {
    setFileHolder(undefined);
    // Reset the input so re-selecting the same file still fires onChange.
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const validateInputs = () => {
    const description = document.getElementById('description');
    if (!description.value || description.value.length < 1) {
      setDescriptionError(true);
      setDescriptionErrorMessage('Please enter an accurate description about your experience');
      notify('Please enter an accurate description about your experience.', 'warning');
      return false;
    }
    setDescriptionError(false);
    setDescriptionErrorMessage('');
    return true;
  };

  const notifyServerMessage = message => {
    const severity = serverErrorSeverity(message);
    if (/guideline/i.test(message)) {
      notify(
        <>
          {message}{' '}
          <Link component={RouterLink} to="/guidelines" color="inherit">
            View guidelines
          </Link>
        </>,
        severity
      );
    } else {
      notify(message, severity);
    }
  };

  const handleSubmit = async event => {
    event.preventDefault();
    // Block re-entry so rapid clicks can't fire multiple create requests.
    if (submittingRef.current) {
      return;
    }
    if (!validateInputs()) {
      return;
    }
    const title = event.currentTarget.title.value;
    const description = event.currentTarget.description.value;
    submittingRef.current = true;
    setSubmitting(true);
    try {
      let documentUrl = null;
      if (fileHolder) {
        const response = await upload({ filename: fileHolder.name });
        const presignedUrl = response.data.s3_url;
        documentUrl = presignedUrl.split('?')[0];
        await axios.put(presignedUrl, fileHolder);
      }
      await createPost({ title, description, document: documentUrl });
      closeProp && closeProp();
    } catch (err) {
      // Moderation failures can flag the title and description separately;
      // surface each as its own popup instead of one merged message.
      const errors = err?.response?.data?.errors;
      if (Array.isArray(errors) && errors.length > 0) {
        errors.forEach(notifyServerMessage);
      } else {
        notifyServerMessage(getServerError(err));
      }
    } finally {
      submittingRef.current = false;
      if (mountedRef.current) {
        setSubmitting(false);
      }
    }
  };

  return (
    <>
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
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            // The Dialog paper sizes to its content, so this stays in vw
            // rather than % (there is no parent width to take a % of).
            width: { xs: '75vw', md: '25vw' },
          }}
        >
          <TextField
            name="title"
            id="title"
            placeholder="Name your experience (optional)"
            fullWidth
            multiline
            variant="outlined"
            sx={{ mb: 3, '& .MuiOutlinedInput-root': { height: 'auto' } }}
          />
          <TextField
            name="description"
            id="description"
            placeholder="Describe your experience"
            fullWidth
            multiline
            minRows={4}
            variant="outlined"
            error={descriptionError}
            helperText={descriptionErrorMessage}
            sx={{ '& .MuiOutlinedInput-root': { height: 'auto' } }}
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
                accept="image/*,application/pdf"
                ref={fileInputRef}
                onChange={event => {
                  setFileHolder(event.target.files[0]);
                }}
              />
            </Button>
            {fileHolder && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ fontSize: 13, color: 'text.secondary' }}>{fileHolder.name}</Box>
                <IconButton size="small" aria-label="remove file" onClick={handleRemoveFile}>
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
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
            <br /> Accepted files: images (JPEG, PNG, and similar) and PDF.
          </FormHelperText>
        </Box>
        <Box>
          <PostButton text={submitting ? 'Posting...' : 'Post'} disabled={submitting} />
        </Box>
      </Box>
      <Notification
        open={notification.open}
        message={notification.message}
        severity={notification.severity}
        onClose={closeNotification}
      />
    </>
  );
}
