from datetime import datetime
import hashlib

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Feedback,
    FeedbackAnalysis,
    Issue,
    IssueFeedback,
)

from services.issue_rules import (
    normalize_severity,
    higher_severity,
)


# ============================================================
# ISSUE KEY
# ============================================================

def generate_issue_key(
    category,
):
    """
    Generate a stable human-readable issue key.

    Example:
        ISSUE-PAYMENT-7F3A91
    """

    normalized = (
        str(category or "OTHER")
        .strip()
        .upper()
    )

    normalized = (
        normalized
        .replace(" ", "-")
        .replace("/", "-")
    )

    fingerprint = hashlib.sha1(
        normalized.encode("utf-8")
    ).hexdigest()[:8].upper()

    return (
        f"ISSUE-{normalized}-{fingerprint}"
    )


# ============================================================
# FIND EXISTING ISSUE
# ============================================================

def find_existing_issue(
    db,
    category,
):
    """
    Find an existing open issue with the same
    operational category.

    This prevents every negative feedback record
    from becoming a separate issue.
    """

    if not category:
        category = "Other"

    issue = db.scalar(
        select(Issue)
        .where(
            Issue.category == category
        )
        .where(
            Issue.status.in_(
                [
                    "open",
                    "investigating",
                    "in_progress",
                ]
            )
        )
        .order_by(
            Issue.updated_at.desc()
        )
    )

    return issue


# ============================================================
# CREATE ISSUE
# ============================================================

def create_issue(
    db,
    feedback,
    analysis,
):
    """
    Create a new operational issue from
    a real analyzed feedback record.
    """

    category = (
        analysis.detected_category
        or "Other"
    )

    severity = normalize_severity(
        analysis.priority
    )

    issue_key = generate_issue_key(
        category
    )

    # Ensure uniqueness
    existing_by_key = db.scalar(
        select(Issue)
        .where(
            Issue.issue_key == issue_key
        )
    )

    if existing_by_key:

        issue_key = (
            f"{issue_key}-"
            f"{feedback.id}"
        )

    title = (
        f"{category} Issue"
    )

    description = (
        "Operational issue automatically "
        "created from customer feedback."
    )

    issue = Issue(
        issue_key=issue_key,
        title=title,
        description=description,
        category=category,
        severity=severity,
        priority_score=(
            analysis.priority_score or 0
        ),
        status="open",
        occurrence_count=1,
    )

    db.add(issue)

    db.flush()

    return issue


# ============================================================
# LINK FEEDBACK TO ISSUE
# ============================================================

def link_feedback_to_issue(
    db,
    issue,
    feedback,
):
    """
    Create the Feedback → Issue relationship.
    """

    existing_link = db.scalar(
        select(IssueFeedback)
        .where(
            IssueFeedback.issue_id
            == issue.id
        )
        .where(
            IssueFeedback.feedback_id
            == feedback.id
        )
    )

    if existing_link:

        return False

    link = IssueFeedback(
        issue_id=issue.id,
        feedback_id=feedback.id,
    )

    db.add(link)

    return True


# ============================================================
# UPDATE EXISTING ISSUE
# ============================================================

def update_existing_issue(
    issue,
    analysis,
):
    """
    Update an issue when new feedback is linked.
    """

    current_severity = normalize_severity(
        issue.severity
    )

    new_severity = normalize_severity(
        analysis.priority
    )

    issue.severity = higher_severity(
        current_severity,
        new_severity,
    )

    issue.priority_score = max(
        issue.priority_score or 0,
        analysis.priority_score or 0,
    )

    issue.occurrence_count = (
        issue.occurrence_count or 0
    ) + 1

    issue.updated_at = datetime.utcnow()


# ============================================================
# PROCESS ONE FEEDBACK
# ============================================================

def process_feedback_into_issue(
    db,
    feedback,
):
    """
    Convert one analyzed feedback record
    into an operational issue relationship.

    Returns:
        issue
        created = True/False
        linked = True/False
    """

    analysis = db.scalar(
        select(FeedbackAnalysis)
        .where(
            FeedbackAnalysis.feedback_id
            == feedback.id
        )
    )

    if analysis is None:

        raise ValueError(
            f"Feedback {feedback.id} "
            "has not been analyzed yet."
        )

    # Positive feedback normally does not create
    # an operational issue.
    if not analysis.is_complaint:

        return {
            "issue": None,
            "created": False,
            "linked": False,
            "reason": "Not a complaint",
        }

    category = (
        analysis.detected_category
        or "Other"
    )

    issue = find_existing_issue(
        db,
        category,
    )

    created = False

    if issue is None:

        issue = create_issue(
            db,
            feedback,
            analysis,
        )

        created = True

    else:

        update_existing_issue(
            issue,
            analysis,
        )

    linked = link_feedback_to_issue(
        db,
        issue,
        feedback,
    )

    return {
        "issue": issue,
        "created": created,
        "linked": linked,
        "reason": None,
    }


# ============================================================
# PROCESS PENDING COMPLAINTS
# ============================================================

def create_issues_from_feedback(
    batch_size=500,
):
    """
    Process real analyzed feedback from MySQL.

    Only feedback that does not already have an
    IssueFeedback relationship is considered.
    """

    with SessionLocal() as db:

        records = db.scalars(
            select(Feedback)
            .join(
                FeedbackAnalysis,
                FeedbackAnalysis.feedback_id
                == Feedback.id,
            )
            .where(
                FeedbackAnalysis.is_complaint
                == True
            )
            .where(
                ~Feedback.id.in_(
                    select(
                        IssueFeedback.feedback_id
                    )
                )
            )
            .limit(batch_size)
        ).all()

        created = 0
        linked = 0
        skipped = 0
        failed = 0

        for feedback in records:

            try:

                result = (
                    process_feedback_into_issue(
                        db,
                        feedback,
                    )
                )

                if result["created"]:
                    created += 1

                if result["linked"]:
                    linked += 1

                if not result["linked"]:
                    skipped += 1

            except Exception as exc:

                failed += 1

                print(
                    f"Issue processing failed "
                    f"for feedback "
                    f"{feedback.id}: {exc}"
                )

        db.commit()

        return {
            "records": len(records),
            "issues_created": created,
            "feedback_linked": linked,
            "skipped": skipped,
            "failed": failed,
        }