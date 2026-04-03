import { Button, Typography } from '@mui/material';
import ArrowRightAltOutlinedIcon from '@mui/icons-material/ArrowRightAltOutlined';
import { Link as RouterLink } from 'react-router-dom';
const PostButton = props => {
  const { text, textSx, buttonSx, to, iconStart, iconEnd, onClick } = props;
  return (
    <>
      <Button
        startIcon={iconStart}
        type="submit"
        endIcon={iconEnd}
        component={to ? RouterLink : 'button'}
        to={to}
        onClick={onClick}
        sx={{
          height: '46px',
          width: 'auto',
          color: '#FFFFFF',
          pt: '4px',
          pl: '12px',
          pb: '4px',
          pr: '12px',
          textTransform: 'none',
          backgroundColor: '#003366',
          '&:hover': {
            bgcolor: '#44619A',
          },
          ...buttonSx,
        }}
      >
        <Typography sx={textSx}>{text ?? 'To be filled'}</Typography>
      </Button>
    </>
  );
};

export default PostButton;
