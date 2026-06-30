import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { useNavigate } from 'react-router-dom';
import { logout } from '../api/api.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function ButtonAppBar() {
  const navigate = useNavigate();
  const { isLoggedIn, logout: clearAuth } = useAuth();

  const handleAuthClick = async () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    try {
      await logout();
    } catch (err) {
      console.error(err);
    }
    clearAuth();
    navigate('/');
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'space-evenly' }}>
      <AppBar position="absolute" sx={{ backgroundColor: 'white' }}>
        <Toolbar>
          <IconButton size="large" edge="start" color="black" aria-label="menu" sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, color: 'black', textAlign: 'center' }}
          >
            Realiti
          </Typography>
          <Button
            onClick={handleAuthClick}
            variant="contained"
            sx={{
              color: 'white',
              backgroundColor: '#313033 ',
              borderColor: '#313033 ',
              '&:hover': {
                color: 'grey',
                borderColor: 'grey',
              },
            }}
          >
            {isLoggedIn ? 'Logout' : 'Signin'}
          </Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
