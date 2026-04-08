# Realiti Backend

* [Local Install](#local-install)
* [Postman](#running-via-postman)
* [Curl](#running-via-curl)
* [Issues](https://github.com/thegolriz/Realiti/issues)

## Local Install

Clone the repo and ensure you have the following installed:
- Docker
- Poetry

### Environment Variables

Create a `.env` file in the root directory. Reference the `docker-compose.yml` for the required database variables. You will also need:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | JWT signing key |
| `S3_BUCKET` | AWS S3 bucket name |
| `S3_REGION` | AWS region (e.g. `us-east-1`) |
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |

There is a `.env_example` available. Update it with your values then rename it:

```bash
mv .env_example .env
```

### Docker

Make sure you are in the root directory (not backend). Then run:

```bash
docker compose up --build -d
```

This will start the Flask backend on port 5001 and PostgreSQL. Poetry dependencies are installed automatically during the build.

Check containers are running with `docker ps`. The backend container is named `realiti` and the database is `realitiDB`.

### Database Setup

Exec into the backend container and run migrations:

```bash
docker exec -it realiti bash
poetry run flask db init
poetry run flask db migrate -m "initial"
poetry run flask db upgrade
```

### Verify

Open a browser or use curl to confirm the server is running:

```
http://localhost:5001/api/hello
```

You should see: `{"message":"Hello from the API"}`

## Running via Postman

Ensure Postman agent is installed and running.

### Auth Endpoints

| Endpoint | Method | Body / Auth |
|----------|--------|-------------|
| `/api/hello` | GET | None |
| `/api/signup` | POST | JSON body (see below) |
| `/api/login` | POST | JSON body (see below) |
| `/api/protected` | GET | Bearer token (access token) |
| `/api/refresh` | POST | Bearer token (refresh token) |
| `/api/logout` | POST/DELETE | None |

#### Example Signup

```json
{
    "email": "test@test.test",
    "first_name": "tester",
    "last_name": "test",
    "password": "12345678"
}
```

Passwords are hashed with scrypt before storage.

#### Example Login

```json
{
    "email": "test@test.test",
    "password": "12345678"
}
```

Returns `access_token` and `refresh_token`. Access token expires in 1 hour.

### S3 Upload Endpoint

| Endpoint | Method | Body / Auth |
|----------|--------|-------------|
| `/api/upload` | POST | Bearer token + JSON body |

#### Example Upload Request

```json
{
    "filename": "photo.jpg"
}
```

Returns a presigned S3 URL. Use this URL to PUT the file directly to S3 from the frontend.

### Post Endpoint

| Endpoint | Method | Body / Auth |
|----------|--------|-------------|
| `/api/post` | POST | Bearer token + JSON body |

#### Example Post Request

```json
{
    "description": "Great experience with this realtor",
    "document": "https://your-bucket.s3.amazonaws.com/1_2026-04-04_photo.jpg"
}
```

The post route runs the uploaded image through AWS Rekognition for content moderation before saving. If the image is flagged as inappropriate, the post is rejected and the image is deleted from S3.

## Running via Curl

```bash
# Hello
curl http://localhost:5001/api/hello

# Signup
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@test.test","first_name":"tester","last_name":"test","password":"12345678"}' \
  http://localhost:5001/api/signup

# Login
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@test.test","password":"12345678"}' \
  http://localhost:5001/api/login

# Upload (requires access token)
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"filename":"photo.jpg"}' \
  http://localhost:5001/api/upload

# Create Post (requires access token)
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"description":"Test post","document":"https://your-bucket.s3.amazonaws.com/1_2026-04-04_photo.jpg"}' \
  http://localhost:5001/api/post

# Protected Route
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5001/api/protected

# Refresh Token
curl -X POST -H "Authorization: Bearer YOUR_REFRESH_TOKEN" \
  http://localhost:5001/api/refresh

# Logout
curl -X POST http://localhost:5001/api/logout
```

## Architecture

The backend is structured as follows:

```
backend/
├── app.py                  # Flask app entry point
├── Dockerfile              # Container build config
├── pyproject.toml          # Poetry dependencies
└── website/
    ├── __init__.py          # App factory (create_app)
    ├── models.py            # SQLAlchemy models (User, Post)
    └── api/
        ├── auth_routes.py   # Signup, login, logout, refresh, protected
        ├── postRoutes.py    # Post creation with moderation check
        ├── s3Routes.py      # Presigned URL generation for S3 uploads
        └── moderationRoute.py  # AWS Rekognition content moderation
```

## Moderation Pipeline

Posts with images go through AWS Rekognition before being saved:

1. Image is uploaded to S3 via presigned URL
2. Rekognition `detect_moderation_labels` analyzes the image
3. If any label has confidence > 70%, the post is rejected and the image is deleted from S3
4. If the image passes, the post is saved to the database
