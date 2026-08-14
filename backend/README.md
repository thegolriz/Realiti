# Realiti Backend

Flask API for [realiti.dev](https://realiti.dev).

- [Local Install](#local-install)
- [Postman](#running-via-postman)
- [Curl](#running-via-curl)
- [Rate Limits](#rate-limits)
- [Tests](#tests)
- [Architecture](#architecture)
- [Moderation Pipeline](#moderation-pipeline)
- [Deployment](#deployment)
- [Issues](https://github.com/thegolriz/Realiti/issues)

## Local Install

Clone the repo and ensure you have the following installed:

- Docker
- Poetry

### Environment Variables

Create a `.env` file in the root directory.

| Variable                  | Description                                          |
| ------------------------- | ---------------------------------------------------- |
| `FLASK_APP`               | Entry point, `app.py`                                |
| `SECRET_KEY`              | Flask secret key                                     |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string                         |
| `JWT_SECRET_KEY`          | JWT signing key                                      |
| `POSTGRES_USER`           | Database user, read by docker-compose                |
| `POSTGRES_PASSWORD`       | Database password, read by docker-compose            |
| `POSTGRES_DB`             | Database name, read by docker-compose                |
| `ANTHROPIC_API_KEY`       | Claude API key for the moderation layer              |
| `S3_BUCKET`               | AWS S3 bucket name                                   |
| `S3_REGION`               | AWS region (e.g. `us-east-1`)                        |
| `AWS_ACCESS_KEY_ID`       | IAM access key                                       |
| `AWS_SECRET_ACCESS_KEY`   | IAM secret key                                       |
| `PYTHONUNBUFFERED`        | Set to `1` so container logs flush immediately       |

These two are optional and only matter in production:

| Variable            | Default | Description                                              |
| ------------------- | ------- | -------------------------------------------------------- |
| `JWT_COOKIE_SECURE` | `false` | Set to `true` to make the refresh cookie HTTPS only      |
| `PROXY_FIX_HOPS`    | `0`     | Number of reverse proxies in front of the app            |

`ANTHROPIC_API_KEY` is required even for local work. The Claude client is built when the module is imported, so the app will not start without it.

There is a `.env_example` available. Update it with your values then rename it:

```bash
mv .env_example .env
```

### Docker

Make sure you are in the root directory. Then run:

```bash
docker compose up --build -d
```

This will start the Flask backend on port 5001 and PostgreSQL. Poetry dependencies are installed automatically during the build.

Check containers are running with `docker ps`. The backend container is named `realiti` and the database is `realitiDB`.

### Database Setup

The `migrations/` folder is committed to the repo, so you do not need to init or generate anything. Exec into the backend container and apply what is already there:

```bash
docker exec -it realiti bash
poetry run flask db upgrade
```

Only run `flask db migrate` when you have actually changed `models.py`. Commit the generated file alongside the model change, or CI will fail on the drift check.

### Verify

Open a browser or use curl to confirm the server is running:

```
http://localhost:5001/api/hello
```

You should see: `{"message":"Hello from the API"}`

## Running via Postman

Ensure Postman agent is installed and running.

All routes are prefixed with `/api`.

### Auth

| Endpoint         | Method      | Body / Auth                    |
| ---------------- | ----------- | ------------------------------ |
| `/api/hello`     | GET         | None                           |
| `/api/signup`    | POST        | JSON body (see below)          |
| `/api/login`     | POST        | JSON body (see below)          |
| `/api/protected` | GET         | Bearer token (access token)    |
| `/api/refresh`   | POST        | Refresh cookie + CSRF header   |
| `/api/logout`    | POST/DELETE | None                           |

#### Example Signup

```json
{
  "email": "test@test.test",
  "first_name": "tester",
  "last_name": "test",
  "password": "12345678"
}
```

Passwords must be at least 8 characters. They are hashed with argon2 before storage. If a stored hash is using older parameters it gets upgraded automatically the next time that user logs in.

#### Example Login

```json
{
  "email": "test@test.test",
  "password": "12345678"
}
```

Returns `access_token` in the body. The refresh token is not in the body, it is set as an httpOnly cookie scoped to `/api/refresh`. Access tokens expire in 15 minutes, refresh tokens in 30 days.

CSRF protection is on for cookies, so `/api/refresh` needs the value of the `csrf_refresh_token` cookie sent back in an `X-CSRF-TOKEN` header. Logout is unauthenticated because its only job is clearing that cookie.

### Account

| Endpoint                | Method | Body / Auth                    |
| ----------------------- | ------ | ------------------------------ |
| `/api/account`          | GET    | Bearer token                   |
| `/api/account/password` | PATCH  | Bearer token + JSON body       |
| `/api/account`          | DELETE | Bearer token + JSON body       |

`GET` returns `id`, `first_name`, `email`, and `is_admin`.

#### Example Password Change

```json
{
  "current_password": "12345678",
  "new_password": "87654321",
  "confirm_password": "87654321"
}
```

#### Example Account Deletion

```json
{
  "password": "12345678"
}
```

Deleting an account takes its posts with it, which also removes every reply, like, and dislike on those posts. Replies the user left on other people's posts are deleted too, and any child replies hanging off them are detached rather than removed, so other people's threads survive.

### Posts

| Endpoint    | Method | Body / Auth                          |
| ----------- | ------ | ------------------------------------ |
| `/api/post` | POST   | Bearer token + JSON body             |
| `/api/post` | GET    | Optional bearer token                |

#### Example Post Request

```json
{
  "title": "Great experience",
  "description": "Great experience with this realtor",
  "document": "https://your-bucket.s3.amazonaws.com/1_2026-04-04_photo.jpg"
}
```

Only `description` is required. `title` and `document` are both optional, and posts without a document skip the image checks.

There are three possible outcomes:

| Status | Meaning                                                                 |
| ------ | ----------------------------------------------------------------------- |
| `200`  | Post created and live                                                   |
| `202`  | Held for review. Saved but hidden until an admin approves it            |
| `400`  | Rejected by moderation. Response has `error`, and `errors` if several   |

`GET /api/post` returns only posts with a `clean` review status. Pass `?userId=<id>` to filter by author, or `?userId=me` to get your own without needing to know your id. Each post comes back with its like and dislike counts, plus `liked` and `disliked` for the calling user if a token was sent.

### Likes and Replies

| Endpoint                 | Method | Body / Auth                 |
| ------------------------ | ------ | --------------------------- |
| `/api/like`              | POST   | Bearer token + `postId`     |
| `/api/dislike`           | POST   | Bearer token + `postId`     |
| `/api/reply`             | POST   | Bearer token + JSON body    |
| `/api/replies/<post_id>` | GET    | None                        |

Likes and dislikes are toggles. Posting the same `postId` twice removes the row and returns `{"liked": false}`.

#### Example Reply

```json
{
  "postId": 1,
  "reply_text": "That was not my experience."
}
```

`parent_reply_id` exists on the model for threading but is not set by this route yet.

### Reports

| Endpoint      | Method | Body / Auth              |
| ------------- | ------ | ------------------------ |
| `/api/report` | POST   | Bearer token + JSON body |

```json
{
  "postId": 1,
  "reason": "This is not accurate",
  "evidence_url": "https://your-bucket.s3.amazonaws.com/1_2026-04-04_proof.jpg"
}
```

`evidence_url` is optional and expects an S3 URL from `/api/upload`.

### Admin

Every route here returns `403` unless the user has `is_admin` set.

| Endpoint                                | Method | Body / Auth              |
| --------------------------------------- | ------ | ------------------------ |
| `/api/admin/review-posts`               | GET    | Bearer token (admin)     |
| `/api/admin/review-posts/<id>/approve`  | POST   | Bearer token (admin)     |
| `/api/admin/review-posts/<id>/reject`   | POST   | Bearer token (admin)     |
| `/api/admin/reports`                    | GET    | Bearer token (admin)     |
| `/api/admin/reports/<id>/resolve`       | POST   | Bearer token (admin)     |

Approving sets the post back to `clean` and it appears in the feed. Rejecting sets it to `removed`.

`/api/admin/reports` lists open reports with the reported post attached. Resolving takes an action:

```json
{
  "action": "uphold"
}
```

`uphold` marks the report upheld and takes the post down. `dismiss` closes the report and leaves the post alone. Anything else is a `400`.

There is no route that grants admin. Flip `is_admin` directly in the database.

### S3 Upload

| Endpoint      | Method | Body / Auth              |
| ------------- | ------ | ------------------------ |
| `/api/upload` | POST   | Bearer token + JSON body |

#### Example Upload Request

```json
{
  "filename": "photo.jpg"
}
```

Returns a presigned S3 URL under `s3_url`, valid for an hour. Use it to PUT the file directly to S3 from the frontend, then send the clean URL (no query params) as `document` on the post. The stored key is prefixed with the user id and a timestamp, so uploads never collide.

## Running via Curl

```bash
# Hello
curl http://localhost:5001/api/hello

# Signup
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"test@test.test","first_name":"tester","last_name":"test","password":"12345678"}' \
  http://localhost:5001/api/signup

# Login. -c writes the refresh cookie to a file so the next call can use it
curl -c cookies.txt -X POST -H "Content-Type: application/json" \
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
  -d '{"title":"Test","description":"Test post","document":"https://your-bucket.s3.amazonaws.com/1_2026-04-04_photo.jpg"}' \
  http://localhost:5001/api/post

# Read the feed
curl http://localhost:5001/api/post

# Like a post (requires access token)
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"postId":1}' \
  http://localhost:5001/api/like

# Protected Route
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:5001/api/protected

# Refresh. -b sends the cookie back, and the CSRF value is pulled out of it.
# awk '{print $7}' grabs the 7th column of the cookie file, which is the value
CSRF=$(grep csrf_refresh_token cookies.txt | awk '{print $7}')
curl -b cookies.txt -X POST -H "X-CSRF-TOKEN: $CSRF" \
  http://localhost:5001/api/refresh

# Logout
curl -c cookies.txt -X POST http://localhost:5001/api/logout
```

## Rate Limits

Two routes are throttled per IP:

| Endpoint      | Limit                                       |
| ------------- | ------------------------------------------- |
| `/api/login`  | 10 per minute, 100 per day (failures only)  |
| `/api/signup` | 5 per hour, 20 per day                      |

The login limiter only counts attempts that come back `401`, so a user who keeps typing their password correctly never gets locked out. Going over returns `429` with `{"error": "Too many attempts made, try again later"}`.

Limits are stored in memory, which means they reset on restart and are per worker process.

## Tests

```bash
poetry run pytest
```

Tests run against a temporary SQLite database, not Postgres, so no containers are needed. `conftest.py` sets dummy secrets and patches out the Claude call, so the suite stays offline and never bills the API. Tests that need to check moderation behavior patch it themselves.

CI runs on every push and pull request:

- `lint.yml` runs flake8, isort, and black on the backend, prettier on the frontend
- `test.yml` runs pytest, then applies every migration from scratch against a real Postgres and fails if `models.py` has drifted from the migrations or if the history has more than one head

## Architecture

```
backend/
├── app.py                  # Flask app entry point
├── Dockerfile              # Container build config
├── pyproject.toml          # Poetry dependencies
├── migrations/             # Alembic migrations, committed
├── tests/                  # pytest suite
└── website/
    ├── __init__.py         # App factory (create_app)
    ├── models.py           # SQLAlchemy models
    ├── security.py         # argon2 hashing and verification
    └── api/
        ├── routes.py           # Hello
        ├── auth_routes.py      # Signup, login, logout, refresh, account
        ├── postRoutes.py       # Post creation and feed
        ├── postLike.py         # Like toggle
        ├── postDislike.py      # Dislike toggle
        ├── repliesRoutes.py    # Replies
        ├── reportRoutes.py     # Reporting a post
        ├── adminRoutes.py      # Review queue and report handling
        ├── s3Routes.py         # Presigned URL generation for S3 uploads
        ├── moderationRoute.py  # Regex screen and AWS Rekognition
        ├── claudeModeration.py # Claude moderation layer
        ├── prompts/            # System prompts for each Claude check
        └── data/               # Common word list for leetspeak detection
```

Models are `User`, `Realtor`, `Post`, `PostLikes`, `PostDislikes`, `Replies`, and `Report`. `Realtor` and the verification fields on `Post` are in the schema but no routes use them yet.

## Moderation Pipeline

Posts run through three layers in order. The first one to reject wins, and each layer is cheaper than the one after it, so most bad posts never reach the paid checks.

**1. Regex screen** on the title and description. Catches profanity, leetspeak, unusual spacing, and prompt injection attempts aimed at the Claude layer below. Leetspeak is normalized and checked against a common word list, so `h3llo` gets flagged but a price like `$450k` does not. A hit returns `400` with copy naming the field that needs fixing.

**2. Rekognition** on the uploaded image. If any moderation label comes back above 70% confidence the image is deleted from S3 and the post is rejected.

**3. Claude** (`claude-haiku-4-5`) runs four checks in order: title, description, media, and whether the media actually matches the description. Each returns a structured verdict of `allow`, `block`, or `needs_review`, so responses are always parseable instead of free text. A `block` is terminal and stops the remaining calls. A `needs_review` does not stop the run, since a later check could still be a hard block, which outranks it.

A blocked post returns `400`. A post that ends on `needs_review` is saved with `review_status` set to `pending_review` and returns `202`. It stays out of the public feed until an admin approves it from the dashboard.

Post review status is one of:

| Status           | Meaning                                          |
| ---------------- | ------------------------------------------------ |
| `clean`          | Public, shows in the feed                        |
| `pending_review` | Hidden, waiting on an admin decision             |
| `removed`        | Taken down by an admin or an upheld report       |

Reports are the last layer. Any user can report a post with evidence, and an upheld report sets the post to `removed`. That is the safety valve for anything the automated layers got wrong.

## Deployment

Production runs at [realiti.dev](https://realiti.dev).

The Dockerfile runs gunicorn, not the Flask dev server. `docker compose` overrides that with `flask run --debug` for local work, so the dev server is local only.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

The prod compose file binds to `127.0.0.1:5001:5000` so the container is only reachable through the reverse proxy in front of it, never directly from the internet.

Two env vars need setting in prod that do not matter locally:

- `JWT_COOKIE_SECURE=true` so the refresh cookie is only sent over HTTPS
- `PROXY_FIX_HOPS` set to the number of proxies in front of the app, otherwise rate limiting sees the proxy's IP for every request instead of the real client

CORS allows `http://localhost:3000` and `https://realiti.dev`. A new frontend origin has to be added in `website/__init__.py`.
