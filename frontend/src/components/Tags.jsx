import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import { UseState, UseEffect } from 'react';
import api from '../api/api.js';

const Tags = props => {
  const [tags, setTags] = useState([]);
  // useEffect = (() =>{
  //   const fetchTags = async
  // })
  const { boxSx } = props;
  return (
    <Autocomplete
      sx={{
        '& .MuiAutocomplete-popupIndicator': {
          padding: '2px',
          height: '100%',
        },
        '& .MuiAutocomplete-popupIndicator svg': {
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
