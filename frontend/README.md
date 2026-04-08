# Realiti Frontend

React + Material UI frontend for the Realiti platform.

## Setup

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`.

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Sign In | User login with JWT auth |
| `/signup` | Sign Up | Account registration |
| `/post` | Create Post | Submit a post with description and optional file upload |
| `/dashboard` | Dashboard | Post feed (in progress) |

## API Integration

All API calls are centralized in `src/api/api.js` using Axios. The base URL points to the Flask backend at `http://localhost:5001/api`.

Available functions:
- `signup(data)` — Register a new account
- `login(data)` — Login and receive JWT tokens
- `upload(data, token)` — Get a presigned S3 URL for file upload
- `createPost(data, token)` — Create a post with description and S3 URL

## Post Submission Flow

1. User fills in description and selects a file
2. Frontend requests a presigned URL from the backend
3. File is uploaded directly to S3 via PUT request
4. Clean S3 URL (without query params) is sent with the post data to the backend
5. Backend runs moderation check before saving

## Project Structure

```
frontend/src/
├── api/
│   └── api.js              # Axios instance and API functions
├── components/
│   └── PostButton.jsx      # Reusable post button
├── pages/
│   ├── Signin.jsx          # Login page
│   ├── Signup.jsx          # Registration page
│   ├── Post.jsx            # Post creation page
│   └── Dashboard.jsx       # Post feed (in progress)
└── shared-theme/           # MUI theme customizations
```
