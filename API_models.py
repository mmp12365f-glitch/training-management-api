from datetime import date as DateType
from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

class TrainingCreate(BaseModel):

    date : DateType
    distance : float = Field(gt=0)
    training_type: str
    moving_time: float = Field(gt=0)
    avg_hr: int = Field(gt=0)
    max_hr: int = Field(gt=0)
    elevation_gain: float = Field(ge=0)
    rpe: int = Field(ge=1, le=10)
    temperature: float | None = None
    notes: str | None = None
    athlete_id:int
    plan_id:int | None = None

class TrainingOut(BaseModel):

    model_config =  ConfigDict(from_attributes=True)

    id: int
    date: DateType
    distance: float
    training_type: str
    moving_time: float
    avg_hr: int
    max_hr: int
    elevation_gain: float
    rpe: int
    temperature: float | None
    notes: str | None
    athlete_id:int
    plan_id:int | None

class TrainingPage(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages:int
    items: list[TrainingOut]

class TrainingUpdate(BaseModel):
    date: DateType | None = None

    distance: float | None = Field(
        default=None,
        gt=0
    )

    training_type: str | None = None

    moving_time: float | None = Field(
        default=None,
        gt=0
    )

    avg_hr: int | None = Field(
        default=None,
        gt=0
    )

    max_hr: int | None = Field(
        default=None,
        gt=0
    )

    elevation_gain: float | None = Field(
        default=None,
        ge=0
    )

    rpe: int | None = Field(
        default=None,
        ge=1,
        le=10
    )

    temperature: float | None = None

    notes: str | None = None

    athlete_id: int | None = None


class AthleteCreate(BaseModel):
    name: str
    age: int | None = None

class AthleteOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    age: int | None

class TrainingPlanCreate(BaseModel):
    athlete_id: int
    name: str
    start_date: DateType
    end_date: DateType
    goal: str | None = None

class TrainingPlanOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    athlete_id: int
    name: str
    start_date: DateType
    end_date: DateType
    goal: str | None


class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str