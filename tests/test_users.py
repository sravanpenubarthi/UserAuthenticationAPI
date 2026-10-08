from app.models import User


# ---------- register ----------
def test_register_success(client, user_payload):
    r = client.post("/register", json=user_payload)
    assert r.status_code == 201
    body = r.json()
    assert body["user_id"] == 1
    assert body["email"] == "john@example.com"
    assert body["role"] == "User"
    assert "password" not in body and "password_hash" not in body
    assert body["created_date"]


def test_register_default_role_is_user(client, user_payload):
    del user_payload["role"]
    assert client.post("/register", json=user_payload).json()["role"] == "User"


def test_register_duplicate_email(client, registered, user_payload):
    r = client.post("/register", json=user_payload)
    assert r.status_code == 409
    assert "already exists" in r.json()["detail"]


def test_register_duplicate_email_case_insensitive(client, registered, user_payload):
    user_payload["email"] = "JOHN@Example.com"
    assert client.post("/register", json=user_payload).status_code == 409


def test_register_invalid_email(client, user_payload):
    user_payload["email"] = "not-an-email"
    assert client.post("/register", json=user_payload).status_code == 422


def test_register_weak_password(client, user_payload):
    user_payload["password"] = "123"
    r = client.post("/register", json=user_payload)
    assert r.status_code == 422


def test_register_missing_full_name_and_email(client):
    assert client.post("/register", json={"password": "Secret@123"}).status_code == 422


def test_register_blank_full_name(client, user_payload):
    user_payload["full_name"] = "   "
    assert client.post("/register", json=user_payload).status_code == 422


def test_register_invalid_role(client, user_payload):
    user_payload["role"] = "SuperAdmin"
    assert client.post("/register", json=user_payload).status_code == 422


def test_register_invalid_phone(client, user_payload):
    user_payload["phone_number"] = "abc"
    assert client.post("/register", json=user_payload).status_code == 422


# ---------- password storage ----------
def test_password_is_hashed_in_db(client, db, user_payload, registered):
    stored = db.query(User).first().password_hash
    assert stored != user_payload["password"]
    assert user_payload["password"] not in stored
    assert stored.startswith("$2")  # bcrypt


# ---------- login ----------
def test_login_success(client, registered, user_payload):
    r = client.post("/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    assert r.status_code == 200
    assert r.json()["message"] == "Login successful"
    assert r.json()["user"]["email"] == "john@example.com"


def test_login_wrong_password(client, registered, user_payload):
    r = client.post("/login", json={"email": user_payload["email"], "password": "WrongPass1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password"


def test_login_unknown_email(client):
    r = client.post("/login", json={"email": "nobody@example.com", "password": "Whatever1"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password"


# ---------- read ----------
def test_get_all_users(client, registered):
    r = client.get("/users")
    assert r.status_code == 200 and len(r.json()) == 1


def test_get_user_by_id(client, registered):
    assert client.get("/users/1").json()["full_name"] == "John Doe"


def test_get_user_not_found(client):
    assert client.get("/users/999").status_code == 404


def test_filter_by_role(client, registered, user_payload):
    admin = {**user_payload, "email": "admin@example.com", "full_name": "Alice Admin", "role": "Admin"}
    client.post("/register", json=admin)
    r = client.get("/users", params={"role": "Admin"})
    assert [u["email"] for u in r.json()] == ["admin@example.com"]


def test_filter_by_invalid_role(client):
    assert client.get("/users", params={"role": "Boss"}).status_code == 422


def test_search_by_name(client, registered, user_payload):
    client.post("/register", json={**user_payload, "email": "jane@example.com", "full_name": "Jane Smith"})
    r = client.get("/users", params={"name": "john"})
    assert [u["full_name"] for u in r.json()] == ["John Doe"]


def test_search_by_name_and_role(client, registered):
    assert len(client.get("/users", params={"name": "John", "role": "User"}).json()) == 1
    assert client.get("/users", params={"name": "John", "role": "Admin"}).json() == []


# ---------- update ----------
def test_update_user(client, registered):
    r = client.put("/users/1", json={"full_name": "John Updated", "role": "Admin"})
    assert r.status_code == 200
    assert r.json()["full_name"] == "John Updated" and r.json()["role"] == "Admin"


def test_update_user_duplicate_email(client, registered, user_payload):
    client.post("/register", json={**user_payload, "email": "other@example.com"})
    assert client.put("/users/2", json={"email": "john@example.com"}).status_code == 409


def test_update_user_empty_body(client, registered):
    assert client.put("/users/1", json={}).status_code == 400


def test_update_user_not_found(client):
    assert client.put("/users/42", json={"full_name": "X"}).status_code == 404


# ---------- password change ----------
def test_change_password(client, registered, user_payload):
    r = client.put("/users/1/password", json={"old_password": user_payload["password"], "new_password": "NewSecret@456"})
    assert r.status_code == 200
    assert client.post("/login", json={"email": user_payload["email"], "password": user_payload["password"]}).status_code == 401
    assert client.post("/login", json={"email": user_payload["email"], "password": "NewSecret@456"}).status_code == 200


def test_change_password_wrong_old(client, registered):
    r = client.put("/users/1/password", json={"old_password": "nope", "new_password": "NewSecret@456"})
    assert r.status_code == 400


def test_change_password_weak_new(client, registered, user_payload):
    r = client.put("/users/1/password", json={"old_password": user_payload["password"], "new_password": "123"})
    assert r.status_code == 422


# ---------- delete ----------
def test_delete_user(client, registered):
    assert client.delete("/users/1").status_code == 204
    assert client.get("/users/1").status_code == 404


def test_delete_user_not_found(client):
    assert client.delete("/users/999").status_code == 404
