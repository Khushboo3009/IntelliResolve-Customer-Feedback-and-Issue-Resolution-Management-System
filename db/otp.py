from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from db.engine import Base


class EmailOTP(Base):

    __tablename__ = "email_otps"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    otp_hash: Mapped[str] = mapped_column(
        String(255),
    )

    purpose: Mapped[str] = mapped_column(
        String(50),
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )