from datetime import datetime
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    org_name: str
    full_name: str
    email: EmailStr
    password: str


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    plan_name: str = "Unlimited"


class ClassCreate(BaseModel):
    title: str
    coach_name: str
    starts_at: datetime
    capacity: int = 20


class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    source: str = "web"
