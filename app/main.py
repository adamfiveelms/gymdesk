from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes import router
from app.core.database import Base, engine, get_db
from app.models.models import Organization, User, Member, ClassSession, Lead, Invoice
from app.services.auth import hash_password

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AdamDesk", version="0.1.0")
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        org = db.scalar(select(Organization).where(Organization.name == "AdamDesk Demo Gym"))
        if org:
            return
        org = Organization(name="AdamDesk Demo Gym")
        db.add(org)
        db.flush()

        db.add(
            User(
                email="owner@adamdesk.app",
                full_name="Demo Owner",
                hashed_password=hash_password("demo1234"),
                role="owner",
                organization_id=org.id,
            )
        )
        db.add_all(
            [
                Member(
                    organization_id=org.id,
                    first_name="Alex",
                    last_name="Stone",
                    email="alex@example.com",
                    plan_name="Unlimited",
                ),
                Member(
                    organization_id=org.id,
                    first_name="Riley",
                    last_name="Chen",
                    email="riley@example.com",
                    plan_name="8x / month",
                ),
            ]
        )
        db.add_all(
            [
                ClassSession(
                    organization_id=org.id,
                    title="CrossFit WOD",
                    coach_name="Jamie",
                    starts_at=datetime.utcnow() + timedelta(hours=2),
                    capacity=24,
                ),
                ClassSession(
                    organization_id=org.id,
                    title="Hyrox Engine",
                    coach_name="Morgan",
                    starts_at=datetime.utcnow() + timedelta(hours=5),
                    capacity=20,
                ),
            ]
        )
        db.add(Lead(organization_id=org.id, full_name="Taylor Reed", email="taylor@lead.com", source="instagram"))
        db.add(Invoice(organization_id=org.id, member_id=1, amount=159.00, status="paid", due_date=datetime.utcnow()))
        db.commit()


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    org = db.scalar(select(Organization).where(Organization.name == "AdamDesk Demo Gym"))
    members = db.scalars(select(Member).where(Member.organization_id == org.id)).all() if org else []
    classes = db.scalars(select(ClassSession).where(ClassSession.organization_id == org.id)).all() if org else []
    leads = db.scalars(select(Lead).where(Lead.organization_id == org.id)).all() if org else []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "org": org,
            "members": members,
            "classes": classes,
            "leads": leads,
        },
    )
