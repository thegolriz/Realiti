import { Avatar } from '@mui/material';
import { useNavigate } from 'react-router-dom';

// Avatar that opens its user's profile. No logged-in check here on purpose:
// /profile/:userId is wrapped in ProtectedRoute, which handles the bounce to
// signin. Falls back to a plain avatar if the payload carried no userId.
const ProfileAvatar = ({ userId, userName, sx }) => {
  const navigate = useNavigate();

  if (!userId) {
    return <Avatar alt={userName} sx={sx} />;
  }

  return (
    <Avatar
      alt={userName}
      onClick={() => navigate(`/profile/${userId}`)}
      sx={{ cursor: 'pointer', '&:hover': { opacity: 0.8 }, ...sx }}
    />
  );
};

export default ProfileAvatar;
