import { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

const MENU_ITEMS = [
  { label: 'Account dashboard', to: '/account' },
  { label: 'Support', to: '/support' },
  { label: 'About', to: '/about' },
  { label: 'Guidelines', to: '/guidelines' },
];

export default function ButtonAppBar() {
  const navigate = useNavigate();
  const { isLoggedIn, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleMenuNavigate = to => {
    setMenuOpen(false);
    navigate(to);
  };

  const handleAuthClick = async () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    await logout();
    navigate('/');
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'space-evenly' }}>
      <AppBar position="absolute" sx={{ backgroundColor: 'white' }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="black"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={() => setMenuOpen(true)}
          >
            <MenuIcon />
          </IconButton>
          <Drawer
            anchor="left"
            open={menuOpen}
            onClose={() => setMenuOpen(false)}
            sx={{
              '& .MuiDrawer-paper': {
                width: '33vw',
                minWidth: 240,
                boxSizing: 'border-box',
              },
            }}
          >
            <Box sx={{ pt: 8 }} role="presentation">
              <List>
                {MENU_ITEMS.map(item => (
                  <ListItem key={item.to} disablePadding>
                    <ListItemButton onClick={() => handleMenuNavigate(item.to)}>
                      <ListItemText primary={item.label} />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>
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
