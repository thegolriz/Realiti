import NavBar from '../components/NavBar.jsx'
import { Box, Stack } from '@mui/material'
import PostCard from '../components/PostCard.jsx'
const Dashboard = () => {
  return (
    <Box>
      <NavBar />
      <Stack direction='column' sx={{ mt: 9, alignItems: 'center', }}>
        <Box sx={{ width: '50%' }}>
          <PostCard />
        </Box>
      </Stack>
    </Box>
  )
}
export default Dashboard;
