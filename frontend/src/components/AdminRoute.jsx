import { Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext.jsx';

// Guard for admin-only pages: waits for auth + the admin flag to resolve,
// then sends non-admins away. The backend also enforces is_admin (403), so
// this is UX, not the security boundary.
export default function AdminRoute({ children }) {
  const { isLoggedIn, isAdmin, bootstrapping, adminResolved } = useAuth();

  if (bootstrapping || !adminResolved) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!isLoggedIn) {
    return <Navigate to="/signin" replace />;
  }
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }

  return children;
}
