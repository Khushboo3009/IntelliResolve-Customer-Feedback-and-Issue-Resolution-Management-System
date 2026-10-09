from sqlalchemy import select, inspect, text
from passlib.context import CryptContext

from db.engine import (
    Base,
    engine,
    SessionLocal,
    ensure_database_exists,
)

# Import ALL models so SQLAlchemy registers their tables.
from db.models import (
    Role,
    Department,
    User,
    Dataset,
    Feedback,
    Issue,
    IssueFeedback,
    IssueInvestigation,
    IssueIntervention,
    InterventionOutcome,
    IngestionJob,
    FeedbackAnalysis,
)

# Register additional tables.
from db.otp import EmailOTP
from db.issue_history import IssueHistory

from config import ADMIN_EMAIL, ADMIN_PASSWORD


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# DEFAULT ROLES
# ============================================================

ROLES = [
    (
        "Administrator",
        "System administrator",
    ),
    (
        "Executive",
        "Executive dashboard access",
    ),
    (
        "Analyst",
        "Issue investigation",
    ),
    (
        "Operations Manager",
        "Operational management",
    ),
    (
        "Department User",
        "General employee",
    ),
]


# ============================================================
# DEFAULT DEPARTMENTS
# ============================================================

DEPARTMENTS = [
    ("Customer Support", ""),
    ("Engineering", ""),
    ("Finance", ""),
    ("Operations", ""),
    ("Product", ""),
    ("Logistics", ""),
    ("Quality", ""),
    ("HR", ""),
]


# ============================================================
# COLUMN DEFINITIONS FOR LEGACY DATABASES
# ============================================================

SCHEMA_COLUMNS = {
    "datasets": {
        "source": "VARCHAR(100) NULL",
        "processed_at": "DATETIME NULL",
    },

    "feedback": {
        "sentiment": "VARCHAR(30) NULL",
        "emotion": "VARCHAR(30) NULL",
        "processed_at": "DATETIME NULL",
        "processing_status": "VARCHAR(30) NULL",
    },

    "issues": {
        "issue_key": "VARCHAR(180) NULL",
        "priority_score": "FLOAT NULL DEFAULT 0",
        "department_id": "INT NULL",
        "assigned_user_id": "INT NULL",
        "sla_deadline": "DATETIME NULL",
        "investigation_started_at": "DATETIME NULL",
        "resolved_at": "DATETIME NULL",
        "closed_at": "DATETIME NULL",
        "resolution_notes": "TEXT NULL",
        "resolution_status": "VARCHAR(50) NULL",
        "updated_at": "DATETIME NULL",
    },

    "issue_investigations": {
        "investigator_id": "INT NULL",
        "root_cause": "TEXT NULL",
        "evidence": "TEXT NULL",
        "findings": "TEXT NULL",
        "status": "VARCHAR(30) NULL",
        "created_at": "DATETIME NULL",
    },

    "issue_interventions": {
        "assigned_department": "VARCHAR(120) NULL",
        "assigned_user_id": "INT NULL",
        "owner": "VARCHAR(120) NULL",
        "intervention_type": "VARCHAR(100) NULL",
        "priority": "VARCHAR(30) NULL",
        "action_plan": "TEXT NULL",
        "status": "VARCHAR(30) NULL",
        "due_date": "DATETIME NULL",
        "started_at": "DATETIME NULL",
        "completed_at": "DATETIME NULL",
        "created_at": "DATETIME NULL",
        "updated_at": "DATETIME NULL",
        "assignment_email_sent_at": "DATETIME NULL",
    },

    "intervention_outcomes": {
        "before_count": "INT NULL DEFAULT 0",
        "after_count": "INT NULL DEFAULT 0",
        "improvement_percentage": "FLOAT NULL DEFAULT 0",
        "remarks": "TEXT NULL",
        "measured_at": "DATETIME NULL",
    },

    "ingestion_jobs": {
        "job_type": "VARCHAR(50) NULL",
        "total_rows": "INT NULL DEFAULT 0",
        "created_at": "DATETIME NULL",
    },

    "feedback_analysis": {
        "category_confidence": "FLOAT NULL DEFAULT 0",
        "priority": "VARCHAR(30) NULL",
        "priority_score": "FLOAT NULL DEFAULT 0",
        "is_complaint": "BOOLEAN NULL DEFAULT 0",
        "evidence": "TEXT NULL",
        "issue_type": "VARCHAR(100) NULL",
        "issue_confidence": "FLOAT NULL DEFAULT 0",
        "processed_at": "DATETIME NULL",
    },
}


# ============================================================
# SCHEMA SYNCHRONIZATION
# ============================================================

def synchronize_schema():
    print("Synchronizing existing schema...")

    inspector = inspect(engine)

    existing_tables = set(
        inspector.get_table_names()
    )

    with engine.begin() as connection:

        for table_name, columns in SCHEMA_COLUMNS.items():

            if table_name not in existing_tables:
                continue

            existing_columns = {
                column["name"]
                for column in inspector.get_columns(
                    table_name
                )
            }

            for column_name, definition in columns.items():

                if column_name in existing_columns:
                    continue

                sql = (
                    f"ALTER TABLE `{table_name}` "
                    f"ADD COLUMN `{column_name}` {definition}"
                )

                print(
                    f"Adding {table_name}.{column_name}"
                )

                connection.execute(
                    text(sql)
                )


# ============================================================
# REPAIR INTERVENTION DATA
# ============================================================

def repair_interventions():

    print("Repairing intervention records...")

    with SessionLocal() as db:

        # At this point the assigned_user_id column exists.
        interventions = db.scalars(
            select(IssueIntervention)
        ).all()

        for item in interventions:

            if not item.assigned_department:
                item.assigned_department = "Operations"

            if not item.owner:
                item.owner = "Unassigned"

            if not item.intervention_type:
                item.intervention_type = (
                    "Operational Task"
                )

            if not item.priority:
                item.priority = "Medium"

            if not item.action_plan:
                item.action_plan = (
                    "Operational action required."
                )

            if not item.status:
                item.status = "open"

        db.commit()


# ============================================================
# REPAIR ISSUE KEYS
# ============================================================

def repair_issue_keys():

    from uuid import uuid4

    print("Repairing issue keys...")

    with SessionLocal() as db:

        issues = db.scalars(
            select(Issue)
        ).all()

        for issue in issues:

            if not issue.issue_key:

                issue.issue_key = (
                    f"ISS-{uuid4().hex[:10].upper()}"
                )

        db.commit()


# ============================================================
# SEED ROLES / DEPARTMENTS
# ============================================================

def seed_roles_and_departments():

    print(
        "Seeding default roles/departments..."
    )

    with SessionLocal() as db:

        for name, description in ROLES:

            role = db.scalar(
                select(Role).where(
                    Role.name == name
                )
            )

            if role is None:

                db.add(
                    Role(
                        name=name,
                        description=description,
                    )
                )

        for name, description in DEPARTMENTS:

            department = db.scalar(
                select(Department).where(
                    Department.name == name
                )
            )

            if department is None:

                db.add(
                    Department(
                        name=name,
                        description=description,
                    )
                )

        db.commit()


# ============================================================
# CREATE ADMIN
# ============================================================

def create_admin():

    if not ADMIN_EMAIL:
        return

    if not ADMIN_PASSWORD:
        return

    with SessionLocal() as db:

        existing = db.scalar(
            select(User).where(
                User.email == ADMIN_EMAIL
            )
        )

        if existing:
            return

        role = db.scalar(
            select(Role).where(
                Role.name == "Administrator"
            )
        )

        if role is None:
            raise RuntimeError(
                "Administrator role was not created."
            )

        admin = User(
            email=ADMIN_EMAIL.strip().lower(),
            full_name="System Administrator",
            password_hash=pwd.hash(
                ADMIN_PASSWORD
            ),
            role_id=role.id,
            active=True,
        )

        db.add(admin)
        db.commit()

        print(
            "Default administrator created."
        )


# ============================================================
# MAIN INITIALIZATION
# ============================================================

def initialize_database():

    print("Checking database...")

    ensure_database_exists()

    print("Creating missing tables...")

    Base.metadata.create_all(
        bind=engine
    )

    synchronize_schema()

    # IMPORTANT:
    # Do not query IssueIntervention before the
    # schema synchronization above has completed.
    repair_issue_keys()

    repair_interventions()

    seed_roles_and_departments()

    create_admin()

    print(
        "Database initialization completed."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    initialize_database()