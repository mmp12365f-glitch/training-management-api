def test_create_training_plan_not_found(
    client,
    training_payload,
    auth_headers
):

    training_payload["plan_id"] = 999999

    response = client.post(
        "/trainings",
        json=training_payload,
        headers=auth_headers
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Training plan not found"
    )


def test_plan_does_not_belong_to_athlete(
    client,
    athlete,
    training_plan,
    auth_headers
):

    second_athlete_response = client.post(
        "/athletes",
        json={
            "name": "Second Athlete",
            "age": 25
        },
        headers=auth_headers
    )

    assert (
        second_athlete_response.status_code
        == 201
    )

    second_athlete = (
        second_athlete_response.json()
    )

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
            "notes": "invalid relationship",

            "athlete_id":
                second_athlete["id"],

            "plan_id":
                training_plan["id"]
        },
        headers=auth_headers
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        ==
        "Training plan does not belong to this athlete"
    )