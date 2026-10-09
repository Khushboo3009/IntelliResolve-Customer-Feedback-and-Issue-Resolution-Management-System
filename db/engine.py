from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)

Base = declarative_base()

# Correct SQLAlchemy URL
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DATABASE,
)

ROOT_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    port=MYSQL_PORT,
)

root_engine = create_engine(ROOT_URL, pool_pre_ping=True)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def ensure_database_exists():
    with root_engine.begin() as conn:
        conn.execute(
            text(
                f"""
                CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """
            )
        )