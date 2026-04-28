def test_create_pin(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "pin@example.com", "username": "pinuser", "password": "password123"},
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/pins",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"title": "My pin", "description": "desc", "is_public": "true"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "My pin"
    assert response.json()["image_url"].startswith("http://test-storage/")


def test_get_pins(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "feed@example.com", "username": "feeduser", "password": "password123"},
    )
    token = register.json()["access_token"]

    client.post(
        "/api/v1/pins",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"title": "Public pin", "description": "desc", "is_public": "true"},
    )

    response = client.get("/api/v1/pins")
    assert response.status_code == 200
    assert len(response.json()) >= 1
