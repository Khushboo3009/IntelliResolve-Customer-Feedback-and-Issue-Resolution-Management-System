from sqlalchemy import select

from db.engine import SessionLocal
from db.models import (
    Issue,
    IssueInvestigation,
)


def get_open_issues():

    with SessionLocal() as db:

        return db.scalars(
            select(Issue).where(
                Issue.status == "open"
            )
        ).all()


def create_investigation(
    issue_id,
    investigator_id,
):

    with SessionLocal() as db:

        existing = db.scalar(
            select(IssueInvestigation).where(
                IssueInvestigation.issue_id == issue_id
            )
        )

        if existing:
            return existing

        investigation = IssueInvestigation(
            issue_id=issue_id,
            investigator_id=investigator_id,
            status="open",
        )

        db.add(investigation)
        db.commit()
        db.refresh(investigation)

        return investigation


def update_investigation(
    investigation_id,
    root_cause,
    evidence,
    findings,
):

    with SessionLocal() as db:

        inv = db.get(
            IssueInvestigation,
            investigation_id,
        )

        inv.root_cause = root_cause
        inv.evidence = evidence
        inv.findings = findings
        inv.status = "completed"

        db.commit()


def get_investigations():

    with SessionLocal() as db:

        return db.scalars(
            select(IssueInvestigation)
        ).all()