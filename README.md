# User Authentication API

REST API built with **FastAPI**, **SQLAlchemy** and **SQLite** for user registration and login.
Passwords are hashed with **bcrypt** and never stored in plain text. (JWT comes in a later task.)

## Project structure
```
user_auth_api/
├── app/
│   ├── main.py          # FastAPI app, router registration
│   ├── config.py        # DB URL, password length rules
│   ├── database.py      # engine, session, get_db
│   ├── models.py        # User model, RoleEnum
│   ├── schemas.py       # Pydantic request/response models
│   ├── crud.py          # DB logic + password hashing/verification
│   ├── exceptions.py    # custom exceptions + handlers
│   └── routers/
│       ├── auth.py      # /register, /login
│       └── users.py     # /users CRUD, search, password change
├── tests/
├── schema.sql
├── postman_collection.json
├── requirements.txt
└── README.md
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
- Swagger UI: http://127.0.0.1:8000/docs
- The SQLite file `users.db` is created automatically on first run.

## Endpoints
| Method | Path | Description | Success |
|---|---|---|---|
| POST | `/register` | Register a user | 201 |
| POST | `/login` | Validate email + password | 200 |
| GET | `/users` | List users (`?role=Admin`, `?name=John`) | 200 |
| GET | `/users/{user_id}` | Get one user | 200 |
| PUT | `/users/{user_id}` | Update name/email/phone/role | 200 |
| PUT | `/users/{user_id}/password` | Change password (needs old password) | 200 |
| DELETE | `/users/{user_id}` | Delete user | 204 |

### Validation rules
- `full_name` and `email` are required; email is validated by Pydantic `EmailStr` and is unique (case-insensitive).
- `password`: 8–64 characters. Stored as a bcrypt hash in `password_hash`.
- `role`: `Admin` or `User` (default `User`).
- `phone_number`: optional, 10–15 digits, optional leading `+`.

### Error codes
| Code | When |
|---|---|
| 400 | Empty update body, wrong old password |
| 401 | Invalid login credentials (same message for unknown email and wrong password) |
| 404 | User not found |
| 409 | Email already exists |
| 422 | Invalid input (bad email, weak password, invalid role, ...) |

### Example
```bash
curl -X POST http://127.0.0.1:8000/register -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@example.com","phone_number":"9876543210","password":"Secret@123","role":"User"}'

curl -X POST http://127.0.0.1:8000/login -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Secret@123"}'
```

## Testing
**Automated:** `pytest -v` (uses an in-memory SQLite DB, covers all scenarios below).

**Postman:** import `postman_collection.json`, start the server, and run the collection in order.

**Scenarios covered:** register, duplicate email, invalid email, weak password, valid login, wrong password, unknown email, get all, get by ID, update, delete, filter by role, search by name, password change.

**Verify passwords are not plain text:**
```bash
sqlite3 users.db "SELECT email, password_hash FROM users;"
```
The `password_hash` column shows a `$2b$...` bcrypt hash, not the password you registered with.

## Notes
- Endpoints are not access-protected yet; role-based protection arrives with JWT.
