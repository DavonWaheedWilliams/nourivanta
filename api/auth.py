import os
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from .database import get_db
from .models import LoginEvent, SecurityProfile, User

JWT_SECRET = os.getenv("NOURIVANTA_JWT_SECRET", "").strip()
JWT_ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)


def require_secret() -> str:
    if len(JWT_SECRET) < 32:
        raise RuntimeError("NOURIVANTA_JWT_SECRET must be set to a random value of at least 32 characters.")
    return JWT_SECRET


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _security_profile(db: Session, user_id: int) -> SecurityProfile:
    profile = db.scalar(select(SecurityProfile).where(SecurityProfile.user_id == user_id))
    if not profile:
        profile = SecurityProfile(user_id=user_id, session_timeout_min=1440)
        db.add(profile)
        db.flush()
    return profile


def authenticate_user(db: Session, login: str, password: str) -> tuple[User | None, str]:
    normalized = login.strip().lower()
    user = db.scalar(select(User).where(or_(User.username == normalized, User.email == normalized)))
    if not user:
        db.add(LoginEvent(user_id=None, login_identifier=normalized[:255], success=False, client_info="NouriVanta Mobile"))
        db.commit()
        return None, "The username, email, or password is incorrect."
    profile = _security_profile(db, user.id)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if profile.locked_until and profile.locked_until > now:
        minutes = max(1, int((profile.locked_until - now).total_seconds() // 60) + 1)
        db.commit()
        return None, f"Too many failed attempts. Try again in about {minutes} minute(s)."
    if profile.locked_until and profile.locked_until <= now:
        profile.locked_until = None
        profile.failed_login_count = 0
    success = verify_password(password, user.password_hash)
    db.add(LoginEvent(user_id=user.id, login_identifier=normalized[:255], success=success, client_info="NouriVanta Mobile"))
    if success:
        profile.failed_login_count = 0
        profile.locked_until = None
        db.commit()
        return user, ""
    profile.failed_login_count = int(profile.failed_login_count or 0) + 1
    if profile.failed_login_count >= 5:
        profile.locked_until = now + timedelta(minutes=15)
    db.commit()
    return None, "The username, email, or password is incorrect."


def make_token(db: Session, user_id: int) -> str:
    secret = require_secret()
    profile = _security_profile(db, user_id)
    timeout_min = max(15, min(int(profile.session_timeout_min or 1440), 10080))
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=timeout_min)}
    db.commit()
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")
    try:
        payload = jwt.decode(credentials.credentials, require_secret(), algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    return user
