import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { useState, useEffect } from 'react';
import { getTags } from '../api/api.js';

const Tags = props => {
  const [tags, setTags] = useState([]);
  const { boxSx, value, onChange } = props;
  useEffect(() => {
    getTags()
      .then(res => setTags(res.data))
      .catch(() => setTags([]));
  }, []);
  return (
    <Autocomplete
      value={value}
      onChange={onChange}
      options={tags}
      sx={{
        '& .MuiAutocomplete-popupIndicator': {
          padding: '2px',
          height: '100%',
        },
        '& .MuiAutocomplete-popupIndicator svg': {
          fontSize: '1rem',
        },
        '& .MuiAutocomplete-clearIndicator': {
          padding: '2px',
          height: '100%',
        },
        '& .MuiAutocomplete-clearIndicator svg': {
          fontSize: '1rem',
        },

        ...boxSx,
      }}
      size="small"
      renderInput={params => <TextField {...params} placeholder="Tag" />}
    />
  );
};

export default Tags;
