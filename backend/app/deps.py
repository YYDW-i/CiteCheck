from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from .db import get_session
from .models import User
from .auth import decode_token

security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    token = creds.credentials
    sub = decode_token(token)
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(User).where(User.email == sub)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user