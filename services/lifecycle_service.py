from datetime import datetime, timedelta

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Issue,
    Department,
    User,
)


# ============================================================
# VALID ISSUE STATES
# ============================================================

ISSUE_STATES = [
    "open",
    "triaged",
    "assigned",
    "investigating",
    "action_required",
    "in_progress",
    "resolved",
    "verified",
    "closed",
]


ALLOWED_TRANSITIONS = {

    "open": [
        "triaged",
    ],

    "triaged": [
        "assigned",
        "investigating",
    ],

    "assigned": [
        "investigating",
    ],

    "investigating": [
        "action_required",
        "in_progress",
        "resolved",
    ],

    "action_required": [
        "in_progress",
        "investigating",
    ],

    "in_progress": [
        "resolved",
        "investigating",
    ],

    "resolved": [
        "verified",
        "in_progress",
    ],

    "verified": [
        "closed",
    ],

    "closed": [],
}


# ============================================================
# SLA RULES
# ============================================================

SLA_HOURS = {
    "critical": 4,
    "high": 12,
    "medium": 24,
    "low": 72,
}


def calculate_sla_deadline(
    severity,
    start_time=None,
):

    severity = str(
        severity or "medium"
    ).lower()

    hours = SLA_HOURS.get(
        severity,
        24,
    )

    if start_time is None:
        start_time = datetime.utcnow()

    return (
        start_time
        + timedelta(hours=hours)
    )


# ============================================================
# VALIDATE TRANSITION
# ============================================================

def validate_transition(
    current_status,
    new_status,
):

    current_status = (
        current_status or "open"
    )

    if new_status not in ISSUE_STATES:

        raise ValueError(
            f"Invalid issue status: "
            f"{new_status}"
        )

    allowed = ALLOWED_TRANSITIONS.get(
        current_status,
        [],
    )

    if new_status not in allowed:

        raise ValueError(
            f"Invalid lifecycle transition: "
            f"{current_status} → {new_status}"
        )


# ============================================================
# CHANGE ISSUE STATUS
# ============================================================

def transition_issue(
    issue_id,
    new_status,
    resolution_notes=None,
):

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:

            raise ValueError(
                f"Issue {issue_id} "
                "does not exist."
            )

        current_status = (
            issue.status or "open"
        )

        validate_transition(
            current_status,
            new_status,
        )

        now = datetime.utcnow()

        issue.status = new_status
        issue.updated_at = now

        # --------------------------------------------
        # INVESTIGATION
        # --------------------------------------------

        if new_status == "investigating":

            if (
                issue.investigation_started_at
                is None
            ):

                issue.investigation_started_at = (
                    now
                )

        # --------------------------------------------
        # RESOLUTION
        # --------------------------------------------

        if new_status == "resolved":

            issue.resolved_at = now

            issue.resolution_status = (
                "resolved"
            )

            if resolution_notes:

                issue.resolution_notes = (
                    resolution_notes
                )

        # --------------------------------------------
        # CLOSURE
        # --------------------------------------------

        if new_status == "closed":

            issue.closed_at = now

            issue.resolution_status = (
                "closed"
            )

        db.commit()

        return {
            "issue_id": issue.id,
            "old_status": current_status,
            "new_status": new_status,
        }


# ============================================================
# ASSIGN DEPARTMENT
# ============================================================

def assign_department(
    issue_id,
    department_id,
):

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:

            raise ValueError(
                "Issue not found."
            )

        department = db.get(
            Department,
            department_id,
        )

        if department is None:

            raise ValueError(
                "Department not found."
            )

        issue.department_id = (
            department_id
        )

        if issue.status == "open":

            issue.status = "triaged"

        issue.updated_at = (
            datetime.utcnow()
        )

        db.commit()

        return issue


# ============================================================
# ASSIGN USER
# ============================================================

def assign_user(
    issue_id,
    user_id,
):

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:

            raise ValueError(
                "Issue not found."
            )

        user = db.get(
            User,
            user_id,
        )

        if user is None:

            raise ValueError(
                "User not found."
            )

        if not user.active:

            raise ValueError(
                "Selected user is inactive."
            )

        issue.assigned_user_id = (
            user_id
        )

        if issue.status in [
            "open",
            "triaged",
        ]:

            issue.status = "assigned"

        issue.updated_at = (
            datetime.utcnow()
        )

        db.commit()

        return issue


# ============================================================
# CREATE / REFRESH SLA
# ============================================================

def assign_sla(
    issue_id,
):

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:

            raise ValueError(
                "Issue not found."
            )

        if issue.sla_deadline is None:

            issue.sla_deadline = (
                calculate_sla_deadline(
                    issue.severity,
                    issue.created_at
                    or datetime.utcnow(),
                )
            )

            issue.updated_at = (
                datetime.utcnow()
            )

            db.commit()

        return issue.sla_deadline


# ============================================================
# SLA STATUS
# ============================================================

def get_sla_status(issue):

    if issue.sla_deadline is None:

        return "Not Assigned"

    if issue.status == "closed":

        if (
            issue.closed_at
            and issue.closed_at
            <= issue.sla_deadline
        ):

            return "Met"

        return "Breached"

    now = datetime.utcnow()

    if now > issue.sla_deadline:

        return "Breached"

    remaining = (
        issue.sla_deadline - now
    )

    if remaining <= timedelta(hours=2):

        return "At Risk"

    return "On Track"