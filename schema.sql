-- SQLite schema (tables are also auto-created by SQLAlchemy on startup)
CREATE TABLE IF NOT EXISTS users (
    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    phone_number  VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,   -- bcrypt hash, never plain text
    role          VARCHAR(5)   NOT NULL CHECK (role IN ('Admin', 'User')),
    created_date  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
