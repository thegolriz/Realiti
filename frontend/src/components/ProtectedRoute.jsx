import { Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext.jsx';

// Gate for pages that require a signed-in user. Public pages (home,
// guidelines, about) are left unwrapped in App.js.
export default function ProtectedRoute({ children }) {
  const { isLoggedIn, bootstrapping } = useAuth();

  // Wait for the on-load refresh to settle before deciding, otherwise a
  // signed-in user reloading a protected page gets bounced to signin during
  // the brief bootstrap window.
  if (bootstrapping) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isLoggedIn) {
    return <Navigate to="/signin" replace />;
  }

  return children;
}
