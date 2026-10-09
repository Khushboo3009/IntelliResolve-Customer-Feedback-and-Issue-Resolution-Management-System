from passlib.context import CryptContext
from sqlalchemy import select
from db.engine import SessionLocal
from db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def authenticate(email: str, password: str):
    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(User.email == email.strip().lower(), User.active == True)
        )
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.name if user.role else "Unknown",
            "department": user.department.name if user.department else "Unassigned",
        }
