from datetime import datetime, timedelta
import hashlib
import random
import smtplib

from email.mime.text import MIMEText

from sqlalchemy import select, delete
from passlib.context import CryptContext

from config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM_EMAIL,
    SMTP_USE_TLS,
)

from db.engine import SessionLocal
from db.models import User, Role, Department
from db.otp import EmailOTP

# ----------------------------------------------------------
# PASSWORD HASHING
# ----------------------------------------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

# ----------------------------------------------------------
# OTP UTILITIES
# ----------------------------------------------------------

def generate_otp():
    return str(random.randint(100000, 999999))

def otp_hash(otp):
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()

# ----------------------------------------------------------
# SEND EMAIL
# ----------------------------------------------------------

def send_email(email, otp, purpose):

    subject = f"IntelliResolve OTP - {purpose}"

    body = f"""
Hello,

Your IntelliResolve verification code is:

{otp}

This code expires in 10 minutes.

Regards,
IntelliResolve Security
"""

    # Development Mode
    if SMTP_USERNAME == "":

        print("=" * 60)
        print("SMTP NOT CONFIGURED")
        print("Recipient :", email)
        print("OTP       :", otp)
        print("=" * 60)

        return True

    try:

        message = MIMEText(body)

        message["Subject"] = subject
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = email

        server = smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
        )

        if SMTP_USE_TLS:
            server.starttls()

        server.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        server.send_message(message)

        server.quit()

        return True

    except Exception as e:

        print("EMAIL ERROR :", e)

        return False

# ----------------------------------------------------------
# CREATE OTP
# ----------------------------------------------------------

def create_and_send_otp(
    email,
    purpose="signup",
):

    otp = generate_otp()

    with SessionLocal() as db:

        db.execute(
            delete(EmailOTP).where(
                EmailOTP.email == email,
                EmailOTP.purpose == purpose,
            )
        )

        db.add(
            EmailOTP(
                email=email,
                otp_hash=otp_hash(otp),
                purpose=purpose,
                expires_at=datetime.utcnow()
                + timedelta(minutes=10),
            )
        )

        db.commit()

    send_email(
        email,
        otp,
        purpose,
    )

    return True

# ----------------------------------------------------------
# VERIFY OTP
# ----------------------------------------------------------

def verify_otp(
    email,
    otp,
    purpose="signup",
):

    with SessionLocal() as db:

        record = db.scalar(
            select(EmailOTP).where(
                EmailOTP.email == email,
                EmailOTP.purpose == purpose,
            )
        )

        if record is None:
            return False

        if record.verified:
            return False

        if record.expires_at < datetime.utcnow():
            return False

        if record.otp_hash != otp_hash(otp):

            record.attempts += 1
            db.commit()

            return False

        record.verified = True

        db.commit()

        return True

# ----------------------------------------------------------
# GET DEPARTMENTS
# ----------------------------------------------------------

def get_departments():

    with SessionLocal() as db:

        return db.scalars(
            select(Department).order_by(
                Department.name
            )
        ).all()

# ----------------------------------------------------------
# CREATE EMPLOYEE
# ----------------------------------------------------------

def create_employee(
    full_name,
    email,
    password,
    department_id,
):

    with SessionLocal() as db:

        exists = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if exists:
            raise ValueError(
                "Employee already exists."
            )

        role = db.scalar(
            select(Role).where(
                Role.name == "Department User"
            )
        )

        if role is None:
            raise RuntimeError(
                "Department User role not found."
            )

        employee = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role_id=role.id,
            department_id=department_id,
            active=True,
        )

        db.add(employee)

        db.commit()

        return employee

# ----------------------------------------------------------
# LOGIN
# ----------------------------------------------------------

def authenticate_user(
    email,
    password,
):

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:
            return None

        if not user.active:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        role = db.get(
            Role,
            user.role_id,
        )

        department = None

        if user.department_id:

            department = db.get(
                Department,
                user.department_id,
            )

        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": role.name,
            "department": (
                department.name
                if department
                else "-"
            ),
        }

# ----------------------------------------------------------
# FORGOT PASSWORD (READY)
# ----------------------------------------------------------

def update_password(
    email,
    new_password,
):

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:
            raise ValueError("Employee not found.")

        user.password_hash = hash_password(
            new_password
        )

        db.commit()

        return True