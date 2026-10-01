import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from database import get_db
from main import app
from Orm_models import Base
from config import settings

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.test_postgres_db,
)


test_engine = create_engine(
    TEST_DATABASE_URL
)


def override_get_db():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def reset_database():

    assert (
        settings.test_postgres_db
        != settings.postgres_db
    )

    Base.metadata.drop_all(test_engine)

    Base.metadata.create_all(test_engine)

    yield

    Base.metadata.drop_all(test_engine)


@pytest.fixture
def client(reset_database):

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def athlete(
    client,
    auth_headers
):
    response = client.post(
        "/athletes",
        json={
            "name": "Test Athlete",
            "age": 23
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def training(
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

    return response.json()


@pytest.fixture
def training_payload(athlete):

    return {
        "date": "2026-09-27",
        "distance": 10,
        "training_type": "easy",
        "moving_time": 45,
        "avg_hr": 145,
        "max_hr": 160,
        "elevation_gain": 30,
        "rpe": 4,
        "temperature": 22,
        "notes": "pytest training",
        "athlete_id": athlete["id"],
        "plan_id": None
    }

@pytest.fixture
def training_plan(
    client,
    athlete,
    auth_headers
):
    response = client.post(
        "/training-plans",
        json={
            "athlete_id": athlete["id"],
            "name": "5000m Test Plan",
            "start_date": "2026-09-01",
            "end_date": "2026-10-01",
            "goal": "Improve 5000m performance"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def many_trainings(
    client,
    athlete,
    auth_headers
):
    trainings = []

    for i in range(12):
        response = client.post(
            "/trainings",
            json={
                "date": "2026-09-27",
                "distance": 10 + i,
                "training_type": "easy",
                "moving_time": 45,
                "avg_hr": 145,
                "max_hr": 160,
                "elevation_gain": 30,
                "rpe": 4,
                "temperature": 22,
                "notes": f"training {i}",
                "athlete_id": athlete["id"],
                "plan_id": None
            },
            headers=auth_headers
        )

        assert response.status_code == 201

        trainings.append(
            response.json()
        )

    return trainings

@pytest.fixture
def user(client):

    response = client.post(
        "/users/register",
        json={
            "username": "test_user",
            "password": "123456"
        }
    )

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def token(client, user):

    response = client.post(
        "/auth/login",
        data={
            "username": "test_user",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    return response.json()[
        "access_token"
    ]

@pytest.fixture
def auth_headers(token):

    return {
        "Authorization":
            f"Bearer {token}"
    }

@pytest.fixture
def second_auth_headers(client):

    register_response = client.post(
        "/users/register",
        json={
            "username": "second_user",
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
            "username": "second_user",
            "password": "123456"
        }
    )

    assert (
        login_response.status_code
        == 200
    )

    token = (
        login_response
        .json()["access_token"]
    )

    return {
        "Authorization":
            f"Bearer {token}"
    }

@pytest.fixture
def second_athlete(
    client,
    second_auth_headers
):
    response = client.post(
        "/athletes",
        json={
            "name": "Second Athlete",
            "age": 25
        },
        headers=second_auth_headers
    )

    assert response.status_code == 201

    return response.json()