def test_create_training_athlete_not_found(
    client,
    auth_headers
):

    response = client.post(
        "/trainings",
        json={
            "date": "2026-09-27",
            "distance": 10,
            "training_type": "easy",
            "moving_time": 45,
            "avg_hr": 145,
            "max_hr": 160,
            "elevation_gain": 30,
            "rpe": 4,
            "temperature": 22,
            "notes": "no athlete",
            "athlete_id": 999999,
            "plan_id": None
        },
        headers=auth_headers
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Athlete not found"
    )

def test_create_athlete_requires_login(
    client,
):

    response = client.post(
        "/athletes",
        json={
            "name": "No Login Athlete",
            "age": 23
        },
    )

    assert response.status_code == 401