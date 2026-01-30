from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, OperationalError
import traceback

from ..db import get_session
from ..models import User
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterIn, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=data.email, password_hash=hash_password(data.password))
    session.add(user)

    try:
        session.commit()
        session.refresh(user)
        return {"ok": True}
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    except OperationalError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/login")
def login(data: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer"}
