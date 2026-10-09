from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.engine import Base


# ============================================================
# ROLE
# ============================================================

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(60),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    users = relationship(
        "User",
        back_populates="role",
    )


# ============================================================
# DEPARTMENT
# ============================================================

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    users = relationship(
        "User",
        back_populates="department",
    )


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    role = relationship(
        "Role",
        back_populates="users",
    )

    department = relationship(
        "Department",
        back_populates="users",
    )


# ============================================================
# DATASET
# ============================================================

class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    row_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    processed_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    duplicate_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="uploaded",
        nullable=False,
    )

    processing_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

# ============================================================
# FEEDBACK
# ============================================================

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
    )

    customer_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    feedback_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    record_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    raw_payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sentiment: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    emotion: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="new",
        nullable=False,
    )

    processing_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    analysis = relationship(
        "FeedbackAnalysis",
        back_populates="feedback",
        uselist=False,
        cascade="all, delete-orphan",
    )


# ============================================================
# ISSUE
# ============================================================

class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    issue_key: Mapped[str | None] = mapped_column(
        String(180),
        unique=True,
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        default="medium",
        nullable=False,
    )

    priority_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
        nullable=False,
    )

    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    sla_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    investigation_started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    resolution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resolution_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# ISSUE / FEEDBACK LINK
# ============================================================

class IssueFeedback(Base):
    __tablename__ = "issue_feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    issue_id: Mapped[int] = mapped_column(
        ForeignKey("issues.id"),
        nullable=False,
    )

    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedback.id"),
        nullable=False,
    )


# ============================================================
# ISSUE INVESTIGATION
# ============================================================

class IssueInvestigation(Base):
    __tablename__ = "issue_investigations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    issue_id: Mapped[int] = mapped_column(
        ForeignKey("issues.id"),
        nullable=False,
    )

    investigator_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    root_cause: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    findings: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# ISSUE INTERVENTION
# ============================================================

class IssueIntervention(Base):
    __tablename__ = "issue_interventions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    issue_id: Mapped[int] = mapped_column(
        ForeignKey("issues.id"),
        nullable=False,
    )

    # Department receiving the task
    assigned_department: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    # Employee receiving the task
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # Display/legacy owner field
    owner: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="",
    )

    # Required by the existing MySQL table
    intervention_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Corrective Action",
    )

    # Required by the existing MySQL table
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Medium",
    )

    action_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
        nullable=False,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    assignment_email_sent_at: Mapped[datetime | None] = mapped_column(
    DateTime,
    nullable=True,
)


# ============================================================
# INTERVENTION OUTCOME
# ============================================================

class InterventionOutcome(Base):
    __tablename__ = "intervention_outcomes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    intervention_id: Mapped[int] = mapped_column(
        ForeignKey("issue_interventions.id"),
        nullable=False,
    )

    metric_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="Issue Occurrence Count",
    )

    before_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    after_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    improvement_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


# ============================================================
# INGESTION JOB
# ============================================================

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    dataset_id: Mapped[int] = mapped_column(
        ForeignKey("datasets.id"),
        nullable=False,
    )

    job_type: Mapped[str] = mapped_column(
        String(50),
        default="ingestion",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )

    total_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    processed_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    successful_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    duplicate_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_rows: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


# ============================================================
# FEEDBACK ANALYSIS
# ============================================================

class FeedbackAnalysis(Base):
    __tablename__ = "feedback_analysis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedback.id"),
        unique=True,
        nullable=False,
    )

    sentiment: Mapped[str] = mapped_column(
        String(20),
        default="Neutral",
        nullable=False,
    )

    sentiment_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    detected_category: Mapped[str] = mapped_column(
        String(100),
        default="General",
        nullable=False,
    )

    category_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        default="Low",
        nullable=False,
    )

    priority_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    is_complaint: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    keywords: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    issue_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    issue_confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    feedback = relationship(
        "Feedback",
        back_populates="analysis",
    )