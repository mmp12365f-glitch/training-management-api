from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Query
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from Orm_models import Training,Athlete,TrainingPlan,func
from API_models import (
    TrainingCreate,
    TrainingOut,
    TrainingUpdate,
    AthleteCreate,
    AthleteOut,
    TrainingPlanCreate,
    TrainingPlanOut,
    TrainingPage,
    UserCreate, 
    UserOut,
    Token
    
)
from sqlalchemy.exc import IntegrityError

from logging_config import logger

import math

from sqlalchemy.exc import IntegrityError

from Orm_models import User
from security import hash_password

from fastapi.security import OAuth2PasswordRequestForm

from Orm_models import User

from security import (
    create_access_token,
    verify_password,
)

from auth import get_current_user

from permissions import (
    get_owned_athlete_or_404,
    get_owned_plan_or_404,
    get_owned_training_or_404,
)

app = FastAPI()

@app.get(
    "/users/me",
    response_model=UserOut
)
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user


def get_training_or_404(
    session: Session,
    training_id: int
):
    training = session.get(
        Training,
        training_id
    )

    if training is None:
        logger.warning(
            'Training not found:id=%s',
            training_id
        )

        raise HTTPException(
            status_code=404,
            detail="Training not found"
        )

    return training

@app.get(
    "/trainings",
    response_model=TrainingPage
)
def get_trainings(
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    offset = (
        page - 1
    ) * page_size

    total = session.scalar(
        select(
            func.count(Training.id)
        )
        .join(
            Athlete,
            Training.athlete_id
            == Athlete.id
        )
        .where(
            Athlete.user_id
            == current_user.id
        )
    )

    total_pages = math.ceil(
        total / page_size
    )

    statement = (
        select(Training)
        .join(
            Athlete,
            Training.athlete_id
            == Athlete.id
        )
        .where(
            Athlete.user_id
            == current_user.id
        )
        .order_by(
            Training.date.desc(),
            Training.id.desc()
        )
        .limit(page_size)
        .offset(offset)
    )

    trainings = session.scalars(
        statement
    ).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": trainings
    }

@app.get(
    "/athletes",
    response_model=list[AthleteOut]
)
def get_athletes(
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    statement = (
        select(Athlete)
        .where(
            Athlete.user_id
            == current_user.id
        )
    )

    return session.scalars(
        statement
    ).all()

@app.get(
    "/training-plans",
    response_model=list[TrainingPlanOut]
)
def get_training_plans(
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    statement = (
        select(TrainingPlan)
        .join(
            Athlete,
            TrainingPlan.athlete_id
            == Athlete.id
        )
        .where(
            Athlete.user_id
            == current_user.id
        )
    )

    return session.scalars(
        statement
    ).all()

@app.get(
    "/trainings/{training_id}",
    response_model=TrainingOut
)
def get_training(
    training_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    return get_owned_training_or_404(
        session,
        training_id,
        current_user.id
    )

@app.get(
    "/athletes/{athlete_id}",
    response_model=AthleteOut
)
def get_athlete(
    athlete_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    statement = (
        select(Athlete)
        .where(
            Athlete.id == athlete_id,
            Athlete.user_id == current_user.id
        )
    )

    athlete = session.scalars(
        statement
    ).first()

    if athlete is None:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        )

    return athlete

@app.get(
    "/training-plans/{plan_id}",
    response_model=TrainingPlanOut
)
def get_training_plan(
    plan_id: int,
    session: Session = Depends(get_db)
):
    plan = session.get(
        TrainingPlan,
        plan_id
    )

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Training plan not found"
        )

    return plan

@app.get("/athletes/{athlete_id}/trainings")
def get_athlete_trainings(
    athlete_id: int,
    session: Session = Depends(get_db)
):
    athlete = session.get(
        Athlete,
        athlete_id
    )

    if athlete is None:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        )

    return {
        "athlete": athlete.name,
        "training_count": len(athlete.trainings),
        "distances": [
            training.distance
            for training in athlete.trainings
        ]
    }

@app.post(
    "/trainings",
    response_model=TrainingOut,
    status_code=201
)
def create_training(
    new_training: TrainingCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    athlete = get_owned_athlete_or_404(
        session,
        new_training.athlete_id,
        current_user.id
    )

    if new_training.plan_id is not None:

        plan = get_owned_plan_or_404(
            session,
            new_training.plan_id,
            current_user.id
        )

        if (
            plan.athlete_id
            != athlete.id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Training plan does not "
                    "belong to this athlete"
                )
            )

    db_training = Training(
        **new_training.model_dump()
    )

    session.add(db_training)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        logger.exception(
            "Failed to create training"
        )

        raise HTTPException(
            status_code=400,
            detail="Database constraint error"
        )

    session.refresh(db_training)

    return db_training

@app.post(
    "/athletes",
    response_model=AthleteOut,
    status_code=201
)
def create_athlete(
    athlete: AthleteCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    db_athlete = Athlete(
        **athlete.model_dump(),
        user_id=current_user.id
    )

    session.add(db_athlete)
    session.commit()
    session.refresh(db_athlete)

    return db_athlete

@app.post(
    "/training-plans",
    response_model=TrainingPlanOut,
    status_code=201
)
def create_training_plan(
    new_plan: TrainingPlanCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    get_owned_athlete_or_404(
        session,
        new_plan.athlete_id,
        current_user.id
    )

    db_plan = TrainingPlan(
        **new_plan.model_dump()
    )

    session.add(db_plan)
    session.commit()
    session.refresh(db_plan)

    return db_plan

@app.post(
    "/users/register",
    response_model=UserOut,
    status_code=201
)
def register_user(
    user: UserCreate,
    session: Session = Depends(get_db)
):
    db_user = User(
        username=user.username,
        password_hash=hash_password(
            user.password
        )
    )

    session.add(db_user)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    session.refresh(db_user)

    return db_user

@app.post(
    "/auth/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db)
):
    statement = (
        select(User)
        .where(
            User.username
            == form_data.username
        )
    )

    user = session.scalars(
        statement
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.put(
    '/trainings/{training_id}',
    response_model=TrainingOut
)
def update_training(
    training_id:int,
    new_data:TrainingCreate,
    session:Session = Depends(get_db)
):
    
    db_training = get_training_or_404(
            session,
            training_id
        )

    data = new_data.model_dump()

    for field, value in data.items():
        setattr(
            db_training,
            field,
            value
        )

    session.commit()
    session.refresh(db_training)
    return db_training

@app.patch(
    "/trainings/{training_id}",
    response_model=TrainingOut
)
def patch_training(
    training_id: int,
    new_data: TrainingUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    db_training = (
        get_owned_training_or_404(
            session,
            training_id,
            current_user.id
        )
    )

    data = new_data.model_dump(
        exclude_unset=True
    )

    target_athlete_id = data.get(
        "athlete_id",
        db_training.athlete_id
    )

    if target_athlete_id is None:
        raise HTTPException(
            status_code=400,
            detail="athlete_id cannot be null"
        )

    get_owned_athlete_or_404(
        session,
        target_athlete_id,
        current_user.id
    )

    target_plan_id = data.get(
        "plan_id",
        db_training.plan_id
    )

    if target_plan_id is not None:

        plan = get_owned_plan_or_404(
            session,
            target_plan_id,
            current_user.id
        )

        if (
            plan.athlete_id
            != target_athlete_id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Training plan does not "
                    "belong to this athlete"
                )
            )

    for field, value in data.items():
        setattr(
            db_training,
            field,
            value
        )

    session.commit()
    session.refresh(db_training)

    return db_training

@app.delete(
    "/trainings/{training_id}"
)
def delete_training(
    training_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    db_training = (
        get_owned_training_or_404(
            session,
            training_id,
            current_user.id
        )
    )

    session.delete(db_training)
    session.commit()

    logger.info(
        "Training deleted: id=%s user_id=%s",
        training_id,
        current_user.id
    )

    return {
        "message": "Training deleted"
    }