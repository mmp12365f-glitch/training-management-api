import pytest

def test_create_training(
    client,
    training_payload,
    auth_headers
):
    response = client.post(
        "/trainings",
        json=training_payload,
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["distance"] == 10
    assert data["rpe"] == 4
    assert (
        data["athlete_id"]
        == training_payload["athlete_id"]
    )



def test_get_training(client, training,auth_headers):

    training_id = training["id"]

    response = client.get(
        f"/trainings/{training_id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == training_id
    assert data["distance"] == 10
    assert data["rpe"] == 4


def test_patch_training(client, training,auth_headers):

    training_id = training["id"]

    patch_response = client.patch(
        f"/trainings/{training_id}",
        json={
            "rpe": 7
        },
        headers=auth_headers
    )

    assert patch_response.status_code == 200

    patch_data = patch_response.json()

    assert patch_data["rpe"] == 7


    get_response = client.get(
        f"/trainings/{training_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 200

    get_data = get_response.json()

    assert get_data["rpe"] == 7


def test_delete_training(client, training,auth_headers):

    training_id = training["id"]

    delete_response = client.delete(
        f"/trainings/{training_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 200

    assert (
        delete_response.json()["message"]
        == "Training deleted"
    )


    get_response = client.get(
        f"/trainings/{training_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404


def test_get_training_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/trainings/999999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_create_training_invalid_rpe(
    client,
    training_payload,
    auth_headers
):
    training_payload["rpe"] = 20

    response = client.post(
        "/trainings",
        json=training_payload,
        headers=auth_headers
    )

    assert response.status_code == 422


def test_create_training_invalid_distance(
    client,
    training_payload,
    auth_headers
):

    training_payload["distance"] = -5

    response = client.post(
        "/trainings",
        json=training_payload,
        headers=auth_headers
    )

    assert response.status_code == 422

def test_create_training_with_plan(
    client,
    training_payload,
    training_plan,
    auth_headers
):

    training_payload["plan_id"] = (
        training_plan["id"]
    )

    response = client.post(
        "/trainings",
        json=training_payload,
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert (
        data["plan_id"]
        == training_plan["id"]
    )


@pytest.mark.parametrize(
    "query_string",
    [
        "?page=0&page_size=10",
        "?page=1&page_size=0",
        "?page=1&page_size=101",
    ]
)
def test_invalid_pagination_params(
    client,
    auth_headers,
    query_string
):
    response = client.get(
        f"/trainings{query_string}",
        headers=auth_headers
    )

    assert response.status_code == 422


def test_training_order_by_date(
    client,
    athlete,
    auth_headers
):
    dates = [
        "2026-09-25",
        "2026-09-27",
        "2026-09-26",
    ]

    for date in dates:
        response = client.post(
            "/trainings",
            json={
                "date": date,
                "distance": 10,
                "training_type": "easy",
                "moving_time": 45,
                "avg_hr": 145,
                "max_hr": 160,
                "elevation_gain": 30,
                "rpe": 4,
                "temperature": 22,
                "notes": "sort test",
                "athlete_id": athlete["id"],
                "plan_id": None
            },
            headers=auth_headers
        )

        assert response.status_code == 201

    response = client.get(
        "/trainings?page=1&page_size=10",
        headers=auth_headers
    )

    assert response.status_code == 200