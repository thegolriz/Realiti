# Realiti

A social hub where consumers and realtors discuss real estate experiences on even ground. No advertising, no ratings, just honest discussions backed by optional supporting evidence.

## What It Does

Users can share their experiences with realtors, supported by uploaded images or documents. Posts without evidence receive a public warning label. Both consumers and realtors can post, but realtors cannot identify private clients. Content is screened through a multi-layer moderation pipeline before going live.

## Tech Stack

| Layer             | Technology               |
| ----------------- | ------------------------ |
| Frontend          | React, Material UI       |
| Backend           | Flask, Python, Poetry    |
| Database          | PostgreSQL               |
| Auth              | JWT (Flask-JWT-Extended) |
| Containerization  | Docker, Docker Compose   |
| File Storage      | AWS S3 (presigned URLs)  |
| Image Moderation  | AWS Rekognition          |
| Hosting (planned) | AWS EC2                  |

## Moderation Pipeline

1. **Pre-processing** — Regex-based filtering for character substitution and obfuscation
2. **AI Screening** — AWS Rekognition checks images for inappropriate content. Posts are scored as pass, fail, or needs review
3. **Community Correction** — Realtors can publicly reply to posts, providing a self-correcting layer

Posts that fail moderation are rejected and the uploaded image is deleted from S3. Edge cases flagged as "needs review" are sent to a manual review queue.

## Project Structure

```
realiti/
├── docker-compose.yml
├── .env
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── README.md              # Backend setup and API docs
│   └── website/
│       ├── __init__.py         # App factory
│       ├── models.py           # User, Post models
│       └── api/
│           ├── auth_routes.py  # Signup, login, logout, refresh
│           ├── postRoutes.py   # Post creation with moderation
│           ├── s3Routes.py     # Presigned URL generation
│           └── moderationRoute.py  # Rekognition integration
└── frontend/
    ├── package.json
    └── src/
        ├── api/api.js          # Axios API client
        ├── pages/              # Signin, Signup, Post, Dashboard
        └── components/         # Reusable UI components
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

# Start containers
docker compose up --build -d

# Run database migrations
docker exec -it realiti bash
poetry run flask db init
poetry run flask db migrate -m "initial"
poetry run flask db upgrade
```

Frontend runs on `http://localhost:3000`, backend on `http://localhost:5001`.

## Author

Anis Golriz — Computer Science, UNC Asheville (2026)
