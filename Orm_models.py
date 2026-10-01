from datetime import date,datetime

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    func,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass

class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    trainings: Mapped[list["Training"]] = relationship(
        back_populates="athlete"
    )

    training_plans: Mapped[list["TrainingPlan"]] = relationship(
        back_populates="athlete"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="athletes"
    )

class Training(Base):

    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    distance: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    training_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    moving_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    avg_hr: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    max_hr: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    elevation_gain: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    rpe: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    temperature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    athlete_id: Mapped[int] = mapped_column(
        ForeignKey("athletes.id")
    )

    athlete: Mapped["Athlete | None"] = relationship(
        back_populates="trainings"
    )

    plan_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("training_plans.id"),
        nullable=True
    )

    plan: Mapped["TrainingPlan | None"] = relationship(
        back_populates="trainings"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    athlete_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("athletes.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    athlete: Mapped["Athlete"] = relationship(
        back_populates="training_plans"
    )

    trainings: Mapped[list["Training"]] = relationship(
        back_populates="plan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    athletes: Mapped[list["Athlete"]] = relationship(
    back_populates="user"
    )