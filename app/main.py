from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes import router
from app.core.database import Base, engine, get_db
from app.models.models import ClassSession, Invoice, Lead, Member, Organization, User
from app.services.auth import hash_password

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="AdamDesk", version="0.1.0")
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def fallback_context(error_message: str) -> dict:
    org = SimpleNamespace(name="AdamDesk Demo Gym")
    members = [
        SimpleNamespace(first_name="Alex", last_name="Stone", email="alex@example.com", plan_name="Unlimited"),
        SimpleNamespace(first_name="Riley", last_name="Chen", email="riley@example.com", plan_name="8x / month"),
    ]
    classes = [
        SimpleNamespace(title="CrossFit WOD", coach_name="Jamie", starts_at="Today 6:00 PM", capacity=24),
        SimpleNamespace(title="Hyrox Engine", coach_name="Morgan", starts_at="Today 8:00 PM", capacity=20),
    ]
    leads = [SimpleNamespace(full_name="Taylor Reed", email="taylor@lead.com", source="instagram")]
    invoices = [SimpleNamespace(id=1, due_date="Today", amount=159.00, status="paid")]

    return {
        "org": org,
        "members": members,
        "classes": classes,
        "leads": leads,
        "invoices": invoices,
        "monthly_revenue": 159.00,
        "runtime_warning": error_message,
    }


@app.on_event("startup")
def startup() -> None:
    try:
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
    except SQLAlchemyError:
        # Keep app booting in serverless environments even if DB init is unavailable.
        return


def build_dashboard_context(db: Session) -> dict:
    try:
        org = db.scalar(select(Organization).where(Organization.name == "AdamDesk Demo Gym"))
        members = db.scalars(select(Member).where(Member.organization_id == org.id)).all() if org else []
        classes = db.scalars(select(ClassSession).where(ClassSession.organization_id == org.id)).all() if org else []
        leads = db.scalars(select(Lead).where(Lead.organization_id == org.id)).all() if org else []
        invoices = db.scalars(select(Invoice).where(Invoice.organization_id == org.id)).all() if org else []
        monthly_revenue = float(sum(invoice.amount for invoice in invoices)) if invoices else 0.0

        return {
            "org": org,
            "members": members,
            "classes": classes,
            "leads": leads,
            "invoices": invoices,
            "monthly_revenue": monthly_revenue,
            "runtime_warning": None,
        }
    except SQLAlchemyError:
        return fallback_context(
            "Database is temporarily unavailable. Showing demo data while the connection recovers."
        )


def render_page(request: Request, db: Session, active_page: str) -> HTMLResponse:
    context = build_dashboard_context(db)
    context["request"] = request
    context["active_page"] = active_page
    return templates.TemplateResponse(request, "index.html", context)


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "dashboard")


@app.get("/members", response_class=HTMLResponse)
def members_page(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "members")


@app.get("/classes", response_class=HTMLResponse)
def classes_page(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "classes")


@app.get("/leads", response_class=HTMLResponse)
def leads_page(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "leads")


@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "billing")


@app.get("/reports", response_class=HTMLResponse)
def reports_page(request: Request, db: Session = Depends(get_db)):
    return render_page(request, db, "reports")
