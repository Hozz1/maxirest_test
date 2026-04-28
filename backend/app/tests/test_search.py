def test_search_pins(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "search@example.com", "username": "searchuser", "password": "password123"},
    )
    token = register.json()["access_token"]

    client.post(
        "/api/v1/pins",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("cat.jpg", b"img-bytes", "image/jpeg")},
        data={"title": "Cute cats", "description": "cat mood", "is_public": "true"},
    )

    response = client.get("/api/v1/pins/search", params={"q": "cat"})

    assert response.status_code == 200
    assert len(response.json()) >= 1
