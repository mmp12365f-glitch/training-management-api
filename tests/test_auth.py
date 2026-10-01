def test_register_user(client):

    response = client.post(
        "/users/register",
        json={
            "username": "test_user",
            "password": "123456"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "test_user"

    assert "password" not in data

    assert "password_hash" not in data


def test_register_duplicate_username(
    client
):

    payload = {
        "username": "same_user",
        "password": "123456"
    }

    first_response = client.post(
        "/users/register",
        json=payload
    )

    assert first_response.status_code == 201


    second_response = client.post(
        "/users/register",
        json=payload
    )

    assert second_response.status_code == 400

    assert (
        second_response.json()["detail"]
        == "Username already exists"
    )


def test_login_success(client):

    register_response = client.post(
        "/users/register",
        json={
            "username": "login_user",
            "password": "123456"
        }
    )

    assert (
        register_response.status_code
        == 201
    )


    login_response = client.post(
        "/auth/login",
        data={
            "username": "login_user",
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data

    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):

    client.post(
        "/users/register",
        json={
            "username": "test_user",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        ==
        "Invalid username or password"
    )


def test_get_current_user(client):

    client.post(
        "/users/register",
        json={
            "username": "me_user",
            "password": "123456"
        }
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "me_user",
            "password": "123456"
        }
    )

    token = (
        login_response
        .json()["access_token"]
    )

    response = client.get(
        "/users/me",
        headers={
            "Authorization":
                f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "me_user"


def test_user_cannot_access_other_users_athlete(
    client,
    auth_headers
):

    register_response = client.post(
        "/users/register",
        json={
            "username": "user_b",
            "password": "123456"
        }
    )

    assert register_response.status_code == 201


    login_response = client.post(
        "/auth/login",
        data={
            "username": "user_b",
            "password": "123456"
        }
    )

    assert login_response.status_code == 200

    user_b_token = (
        login_response
        .json()["access_token"]
    )

    user_b_headers = {
        "Authorization":
            f"Bearer {user_b_token}"
    }


    athlete_response = client.post(
        "/athletes",
        json={
            "name": "User B Athlete",
            "age": 25
        },
        headers=user_b_headers
    )

    assert athlete_response.status_code == 201

    user_b_athlete = (
        athlete_response.json()
    )


    response = client.get(
        f"/athletes/{user_b_athlete['id']}",
        headers=auth_headers
    )

    assert response.status_code == 404



def test_cannot_create_training_for_other_user(
    client,
    auth_headers,
    second_athlete
):
    response = client.post(
        "/trainings",
        json={
            "date": "2026-09-28",
            "distance": 10,
            "training_type": "easy",
            "moving_time": 45,
            "avg_hr": 145,
            "max_hr": 160,
            "elevation_gain": 20,
            "rpe": 4,
            "temperature": 22,
            "notes": "authorization test",
            "athlete_id": second_athlete["id"],
            "plan_id": None
        },
        headers=auth_headers
    )

    assert response.status_code == 404

def test_cannot_get_other_users_training(
    client,
    auth_headers,
    second_auth_headers,
    second_athlete
):
    create_response = client.post(
        "/trainings",
        json={
            "date": "2026-09-28",
            "distance": 10,
            "training_type": "easy",
            "moving_time": 45,
            "avg_hr": 145,
            "max_hr": 160,
            "elevation_gain": 20,
            "rpe": 4,
            "temperature": 22,
            "notes": "user b training",
            "athlete_id": second_athlete["id"],
            "plan_id": None
        },
        headers=second_auth_headers
    )

    assert create_response.status_code == 201

    training = create_response.json()

    response = client.get(
        f"/trainings/{training['id']}",
        headers=auth_headers
    )

    assert response.status_code == 404