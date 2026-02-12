from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="owner")
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))


class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    plan_name: Mapped[str] = mapped_column(String(80), default="Unlimited")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassSession(Base):
    __tablename__ = "class_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    coach_name: Mapped[str] = mapped_column(String(120))
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer, default=20)


class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    class_session_id: Mapped[int] = mapped_column(ForeignKey("class_sessions.id"))
    attended: Mapped[bool] = mapped_column(Boolean, default=False)


class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(32), default="paid")
    due_date: Mapped[datetime] = mapped_column(DateTime)


class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120))
    source: Mapped[str] = mapped_column(String(80), default="web")
    stage: Mapped[str] = mapped_column(String(32), default="new")
