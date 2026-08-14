# Realiti

A social hub where consumers and realtors discuss real estate experiences on even ground. No advertising, no ratings, just honest discussions backed by optional supporting evidence.

Live at [realiti.dev](https://realiti.dev).

## What It Does

Users can share their experiences with realtors, supported by uploaded images or documents. Both consumers and realtors can post, but realtors cannot identify private clients. Content is screened through a multi-layer moderation pipeline before going live.

## Tech Stack

| Layer            | Stack                          |
| ---------------- | ------------------------------ |
| Frontend         | React, Material UI             |
| Backend          | Flask, Python, Poetry          |
| Database         | PostgreSQL                     |
| Auth             | JWT (Flask-JWT-Extended)       |
| Password Hashing | argon2                         |
| Rate Limiting    | Flask-Limiter                  |
| Containerization | Docker, Docker Compose         |
| File Storage     | AWS S3 (presigned URLs)        |
| Image Moderation | AWS Rekognition                |
| Text Moderation  | Claude API (claude-haiku-4-5)  |
| WSGI Server      | gunicorn                       |
| CI               | GitHub Actions                 |
| Hosting          | AWS EC2                        |

## Moderation Pipeline

1. **Pre-processing**: Regex-based filtering for character substitution and obfuscation
2. **AI Screening**: AWS Rekognition checks images for inappropriate content. Posts are scored as pass, fail, or needs review.
    Then claude API gets called. It checks the title, description, image/document giving a Pass/Fail or needs review.
    Pass/Fail dictates a post, needs review sends it to admin dashboard for final decision, holding the post until reviewed.
3. **Community Correction**: Realtors and other users can publicly reply to posts and report them, providing a self-correcting layer.

Posts that fail moderation are rejected and the uploaded image is deleted from S3. Edge cases flagged as "needs review" are sent to a manual review queue.

See [backend/README.md](backend/README.md#moderation-pipeline) for how each layer actually works.

## Status

The site is live and running in a test period, with a notice to that effect on the dashboard.

Still in progress:

- Realtor verification. The `Realtor` model and the verification fields on `Post` are in the schema, but no routes use them yet
- Post verification. The direction is a check on posts backed by supporting evidence, rather than a warning on posts without it
- Threaded replies. `parent_reply_id` is on the model but the reply route does not set it

## Project Structure

```
realiti/
├── docker-compose.yml          # Local dev
├── docker-compose.prod.yml     # Production
├── .env
├── .github/workflows/          # Lint and test CI
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── README.md               # Backend setup and API docs
│   ├── migrations/             # Alembic migrations, committed
│   ├── tests/                  # pytest suite
│   └── website/
│       ├── __init__.py         # App factory
│       ├── models.py           # User, Realtor, Post, likes, replies, reports
│       ├── security.py         # argon2 hashing
│       └── api/
│           ├── auth_routes.py      # Signup, login, logout, refresh, account
│           ├── postRoutes.py       # Post creation and feed
│           ├── postLike.py         # Like toggle
│           ├── postDislike.py      # Dislike toggle
│           ├── repliesRoutes.py    # Replies
│           ├── reportRoutes.py     # Reporting a post
│           ├── adminRoutes.py      # Review queue and report handling
│           ├── s3Routes.py         # Presigned URL generation
│           ├── moderationRoute.py  # Regex screen and Rekognition
│           └── claudeModeration.py # Claude moderation layer
└── frontend/
    ├── package.json
    └── src/
        ├── api/api.js          # Axios API client
        ├── context/            # AuthContext
        ├── pages/              # Signin, Signup, Post, Dashboard, Profile,
        │                       # Account, AdminDashboard, About, Contact,
        │                       # Guidelines
        ├── components/         # Reusable UI components
        └── shared-theme/       # MUI theme customizations
```

## Getting Started

See [backend/README.md](backend/README.md) for full setup instructions, environment variables, and API documentation.

### Quick Start

```bash
# Clone the repo
git clone https://github.com/thegolriz/Realiti.git
cd Realiti

# Set up environment variables
mv .env_example .env
# Edit .env with your values

# Start the backend and database
docker compose up --build -d

# Apply migrations (they are committed, so no init or migrate needed)
docker exec -it realiti bash
poetry run flask db upgrade
exit

# Start the frontend
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`, backend on `http://localhost:5001`.

The frontend calls the API at a relative `/api` path. In development that works because `package.json` sets `"proxy": "http://localhost:5001"`, which is dev only and does not apply to a production build.

Auth is split across two tokens. The access token lives in memory and is sent as a bearer header, while the refresh token is an httpOnly cookie scoped to `/api/refresh`. An Axios interceptor in `src/api/api.js` refreshes the access token when it expires.

## Author

Anis Golriz, Computer Science, UNC Asheville (2026)
