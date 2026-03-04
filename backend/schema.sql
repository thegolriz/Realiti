CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    first_name TEXT not NULL,
    last_name TEXT not NULL,
    email TEXT not NULL UNIQUE,
    password TEXT not NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_admin BOOLEAN DEFAULT FALSE
)
