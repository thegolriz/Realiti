import NavBar from '../components/NavBar.jsx'
import { Box, Stack } from '@mui/material'
import PostCard from '../components/PostCard.jsx'
import { useState, useEffect } from 'react'
import axios from 'axios';

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [posts, setPosts] = useState([])
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const { data: response } = await axios.get('/post')
        setPosts(response)
      } catch (error) {
        console.error(error.message)
      }
      setLoading(false)
    }
    fetchData()
  }, [])
  console.log("Posts here\n", posts)
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
