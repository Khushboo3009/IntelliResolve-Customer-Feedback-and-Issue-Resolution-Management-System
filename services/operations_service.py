from datetime import datetime

from sqlalchemy import (
    select,
    func,
)

from db.engine import SessionLocal

from db.models import (
    Issue,
    Feedback,
    IssueIntervention,
    InterventionOutcome,
    IngestionJob,
    Department,
)


# ============================================================
# OPERATIONS KPIs
# ============================================================

def get_operations_kpis():

    with SessionLocal() as db:

        total_feedback = db.scalar(
            select(
                func.count(
                    Feedback.id
                )
            )
        ) or 0

        total_issues = db.scalar(
            select(
                func.count(
                    Issue.id
                )
            )
        ) or 0

        active_issues = db.scalar(
            select(
                func.count(
                    Issue.id
                )
            )
            .where(
                Issue.status.notin_(
                    [
                        "resolved",
                        "closed",
                    ]
                )
            )
        ) or 0

        critical_issues = db.scalar(
            select(
                func.count(
                    Issue.id
                )
            )
            .where(
                Issue.severity
                == "critical"
            )
            .where(
                Issue.status.notin_(
                    [
                        "resolved",
                        "closed",
                    ]
                )
            )
        ) or 0

        resolved_issues = db.scalar(
            select(
                func.count(
                    Issue.id
                )
            )
            .where(
                Issue.status.in_(
                    [
                        "resolved",
                        "closed",
                    ]
                )
            )
        ) or 0

        open_interventions = db.scalar(
            select(
                func.count(
                    IssueIntervention.id
                )
            )
            .where(
                IssueIntervention.status
                .in_(
                    [
                        "open",
                        "in_progress",
                    ]
                )
            )
        ) or 0

        breached_sla = db.scalar(
            select(
                func.count(
                    Issue.id
                )
            )
            .where(
                Issue.sla_deadline
                < datetime.utcnow()
            )
            .where(
                Issue.status.notin_(
                    [
                        "resolved",
                        "closed",
                    ]
                )
            )
        ) or 0

        resolution_rate = 0

        if total_issues:

            resolution_rate = round(
                (
                    resolved_issues
                    / total_issues
                ) * 100,
                2,
            )

        return {

            "total_feedback":
                total_feedback,

            "total_issues":
                total_issues,

            "active_issues":
                active_issues,

            "critical_issues":
                critical_issues,

            "resolved_issues":
                resolved_issues,

            "open_interventions":
                open_interventions,

            "sla_breaches":
                breached_sla,

            "resolution_rate":
                resolution_rate,
        }


# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================

def get_department_performance():

    with SessionLocal() as db:

        departments = db.scalars(
            select(
                Department
            )
            .order_by(
                Department.name
            )
        ).all()

        results = []

        for department in departments:

            total = db.scalar(
                select(
                    func.count(
                        Issue.id
                    )
                )
                .where(
                    Issue.department_id
                    == department.id
                )
            ) or 0

            active = db.scalar(
                select(
                    func.count(
                        Issue.id
                    )
                )
                .where(
                    Issue.department_id
                    == department.id
                )
                .where(
                    Issue.status.notin_(
                        [
                            "resolved",
                            "closed",
                        ]
                    )
                )
            ) or 0

            critical = db.scalar(
                select(
                    func.count(
                        Issue.id
                    )
                )
                .where(
                    Issue.department_id
                    == department.id
                )
                .where(
                    Issue.severity
                    == "critical"
                )
            ) or 0

            results.append(
                {
                    "department":
                        department.name,

                    "total":
                        total,

                    "active":
                        active,

                    "critical":
                        critical,
                }
            )

        return results


# ============================================================
# ISSUE HEALTH
# ============================================================

def get_issue_health():

    with SessionLocal() as db:

        issues = db.scalars(
            select(
                Issue
            )
            .where(
                Issue.status.notin_(
                    [
                        "resolved",
                        "closed",
                    ]
                )
            )
            .order_by(
                Issue.priority_score.desc(),
                Issue.occurrence_count.desc(),
            )
            .limit(100)
        ).all()

        return issues


# ============================================================
# RECENT JOBS
# ============================================================

def get_recent_jobs(
    limit=10,
):

    with SessionLocal() as db:

        return db.scalars(
            select(
                IngestionJob
            )
            .order_by(
                IngestionJob.created_at.desc()
            )
            .limit(limit)
        ).all()