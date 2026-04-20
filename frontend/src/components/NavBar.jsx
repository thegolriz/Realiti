import AppBar from '@mui/material/AppBar';
import CreatePostButton from './CreatePostButton.jsx'
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';

export default function ButtonAppBar() {
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
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'black', textAlign: 'center' }}>
            Realiti
          </Typography>
          <Button
            href="/signin"
            variant='contained' sx={{
              color: 'white',
              backgroundColor: '#313033 ',
              borderColor: '#313033 ',
              '&:hover': {
                color: 'grey',
                borderColor: 'grey',
              }
            }}>Signin</Button>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

