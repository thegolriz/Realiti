import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

const EXPERIENCE_OPTIONS = ['terrible', 'bad', 'average', 'good', 'great'];

const ExperienceTag = props => {
  const { boxSx } = props;
  return (
    <Autocomplete
      options={EXPERIENCE_OPTIONS}
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
      renderInput={params => <TextField {...params} placeholder="Experience" />}
    />
  );
};

export default ExperienceTag;
