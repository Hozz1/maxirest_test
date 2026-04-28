def test_register_success(client) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "password123"},
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_register_duplicate_email(client) -> None:
    payload = {"email": "dup@example.com", "username": "dupuser", "password": "password123"}
    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_success(client) -> None:
    register_payload = {"email": "login@example.com", "username": "loginuser", "password": "password123"}
    client.post("/api/v1/auth/register", json=register_payload)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_current_user(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "username": "meuser", "password": "password123"},
    )
    token = register_response.json()["access_token"]

    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
