"""Application settings."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 64  # bcrypt only uses the first 72 bytes
APP_TITLE = "User Authentication API"
APP_VERSION = "1.0.0"
