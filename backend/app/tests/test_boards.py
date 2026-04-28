def test_create_board(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "board@example.com", "username": "boarduser", "password": "password123"},
    )
    token = register.json()["access_token"]

    response = client.post(
        "/api/v1/boards",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Inspiration", "description": "Ideas", "is_public": True},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Inspiration"


def test_add_pin_to_board(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "board-pin@example.com", "username": "boardpin", "password": "password123"},
    )
    token = register.json()["access_token"]

    pin_resp = client.post(
        "/api/v1/pins",
        headers={"Authorization": f"Bearer {token}"},
        files={"image": ("photo.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"title": "Pin for board", "is_public": "true"},
    )
    pin_id = pin_resp.json()["id"]

    board_resp = client.post(
        "/api/v1/boards",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "My board", "description": None, "is_public": True},
    )
    board_id = board_resp.json()["id"]

    response = client.post(
        f"/api/v1/boards/{board_id}/pins/{pin_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
