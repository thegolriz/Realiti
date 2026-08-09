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
  { label: 'Home', to: '/' },
  { label: 'Admin dashboard', to: '/admin', adminOnly: true },
  { label: 'Profile', to: '/profile/me', requiresAuth: true },
  { label: 'Account dashboard', to: '/account', requiresAuth: true },
  { label: 'About', to: '/about' },
  { label: 'Guidelines', to: '/guidelines' },
  { label: 'Contact', to: '/contact' },
];

export default function ButtonAppBar() {
  const navigate = useNavigate();
  const { isLoggedIn, isAdmin, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuItems = MENU_ITEMS.filter(
    item => (isLoggedIn || !item.requiresAuth) && (!item.adminOnly || isAdmin)
  );

  const handleMenuNavigate = to => {
    setMenuOpen(false);
    navigate(to);
  };

  const handleAuthClick = async () => {
    if (!isLoggedIn) {
      navigate('/signin');
      return;
    }
    // Move to the public dashboard before clearing auth, so the ProtectedRoute
    // guard doesn't bounce us to signin as isLoggedIn flips.
    navigate('/');
    await logout();
  };

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', justifyContent: 'space-evenly' }}>
      <AppBar position="absolute" sx={{ bgcolor: 'background.paper', color: 'text.primary' }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
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
                {menuItems.map(item => (
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
            onClick={() => navigate('/')}
            sx={{
              flexGrow: 1,
              color: 'text.primary',
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': { opacity: 0.7 },
            }}
          >
            Realiti
          </Typography>
          <Button
            onClick={handleAuthClick}
            variant="contained"
            sx={{
              color: 'background.paper',
              bgcolor: 'text.primary',
              '&:hover': {
                bgcolor: 'text.secondary',
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
