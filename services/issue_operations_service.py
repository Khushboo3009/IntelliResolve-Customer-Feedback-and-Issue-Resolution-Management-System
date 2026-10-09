from datetime import datetime

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import Issue

from db.issue_history import IssueHistory


VALID_STATUSES = {
    "new",
    "triaged",
    "assigned",
    "investigating",
    "intervention_planned",
    "intervention_active",
    "resolution_pending",
    "resolved",
    "verification",
    "closed",
    "reopened",
}


def change_issue_status(
    issue_id,
    new_status,
    user_id=None,
    comment=None,
):

    new_status = new_status.lower().strip()

    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid issue status: {new_status}"
        )

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:
            raise ValueError(
                "Issue not found."
            )

        previous_status = issue.status

        if previous_status == new_status:
            return issue

        issue.status = new_status

        history = IssueHistory(
            issue_id=issue.id,
            changed_by=user_id,
            previous_status=previous_status,
            new_status=new_status,
            comment=comment,
            created_at=datetime.utcnow(),
        )

        db.add(history)

        db.commit()

        db.refresh(issue)

        return issue


def assign_issue(
    issue_id,
    department_id=None,
    user_id=None,
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

        if department_id is not None:
            issue.department_id = department_id

        if user_id is not None:
            issue.assigned_user_id = user_id

        if issue.status in [
            "new",
            "triaged",
        ]:
            issue.status = "assigned"

        db.commit()

        db.refresh(issue)

        return issue