from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from Orm_models import Athlete, Training, TrainingPlan


def get_owned_athlete_or_404(
    session: Session,
    athlete_id: int,
    user_id: int
) -> Athlete:

    statement = (
        select(Athlete)
        .where(
            Athlete.id == athlete_id,
            Athlete.user_id == user_id
        )
    )

    athlete = session.scalar(statement)

    if athlete is None:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        )

    return athlete

def get_owned_plan_or_404(
    session: Session,
    plan_id: int,
    user_id: int
) -> TrainingPlan:

    statement = (
        select(TrainingPlan)
        .join(
            Athlete,
            TrainingPlan.athlete_id
            == Athlete.id
        )
        .where(
            TrainingPlan.id == plan_id,
            Athlete.user_id == user_id
        )
    )

    plan = session.scalar(statement)

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Training plan not found"
        )

    return plan


def get_owned_training_or_404(
    session: Session,
    training_id: int,
    user_id: int
) -> Training:

    statement = (
        select(Training)
        .join(
            Athlete,
            Training.athlete_id
            == Athlete.id
        )
        .where(
            Training.id == training_id,
            Athlete.user_id == user_id
        )
    )

    training = session.scalar(statement)

    if training is None:
        raise HTTPException(
            status_code=404,
            detail="Training not found"
        )

    return training