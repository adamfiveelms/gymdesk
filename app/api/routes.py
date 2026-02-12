from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Organization, User, Member, ClassSession, Booking, Invoice, Lead
from app.schemas.schemas import UserCreate, Token, MemberCreate, ClassCreate, LeadCreate
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api")


@router.post("/auth/register", response_model=Token)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already used")

    org = Organization(name=payload.org_name)
    db.add(org)
    db.flush()
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role="owner",
        organization_id=org.id,
    )
    db.add(user)
    db.commit()

    return Token(access_token=create_access_token(str(user.id)))


@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/dashboard/{organization_id}")
def dashboard(organization_id: int, db: Session = Depends(get_db)):
    members = db.scalar(select(func.count()).select_from(Member).where(Member.organization_id == organization_id))
    leads = db.scalar(select(func.count()).select_from(Lead).where(Lead.organization_id == organization_id))
    upcoming_classes = db.scalar(
        select(func.count()).select_from(ClassSession).where(
            ClassSession.organization_id == organization_id,
            ClassSession.starts_at >= datetime.utcnow(),
        )
    )
    mrr = db.scalar(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.organization_id == organization_id,
            Invoice.status == "paid",
            Invoice.due_date >= datetime.utcnow() - timedelta(days=30),
        )
    )
    return {
        "members": members,
        "leads": leads,
        "upcoming_classes": upcoming_classes,
        "mrr_30d": float(mrr or 0),
    }


@router.post("/organizations/{organization_id}/members")
def create_member(organization_id: int, payload: MemberCreate, db: Session = Depends(get_db)):
    member = Member(organization_id=organization_id, **payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/organizations/{organization_id}/members")
def list_members(organization_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(Member).where(Member.organization_id == organization_id)).all()


@router.post("/organizations/{organization_id}/classes")
def create_class(organization_id: int, payload: ClassCreate, db: Session = Depends(get_db)):
    session = ClassSession(organization_id=organization_id, **payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/organizations/{organization_id}/classes")
def list_classes(organization_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(ClassSession).where(ClassSession.organization_id == organization_id)).all()


@router.post("/organizations/{organization_id}/leads")
def create_lead(organization_id: int, payload: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(organization_id=organization_id, **payload.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/organizations/{organization_id}/leads")
def list_leads(organization_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(Lead).where(Lead.organization_id == organization_id)).all()


@router.post("/organizations/{organization_id}/bookings")
def create_booking(organization_id: int, member_id: int, class_session_id: int, db: Session = Depends(get_db)):
    booking = Booking(
        organization_id=organization_id, member_id=member_id, class_session_id=class_session_id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
