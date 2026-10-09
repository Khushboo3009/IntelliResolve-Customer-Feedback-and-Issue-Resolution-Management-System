from collections import defaultdict
from uuid import uuid4

from sqlalchemy import select

from db.engine import SessionLocal
from db.models import (
    Feedback,
    Issue,
    IssueFeedback,
)


# ============================================================
# RULES
# ============================================================

CRITICAL_WORDS = [
    "fraud",
    "security",
    "breach",
    "data leak",
    "unsafe",
]

HIGH_WORDS = [
    "payment",
    "failed",
    "refund",
    "delay",
    "broken",
]

CATEGORY_KEYWORDS = {
    "Delivery": [
        "delivery",
        "late",
        "shipment",
    ],
    "Payment": [
        "payment",
        "refund",
        "transaction",
    ],
    "Support": [
        "support",
        "service",
        "agent",
    ],
    "Quality": [
        "quality",
        "defect",
        "broken",
    ],
    "Technical": [
        "bug",
        "error",
        "crash",
    ],
}


# ============================================================
# ISSUE DETECTION
# ============================================================

def detect_issue(text: str):
    """
    Detect the most relevant issue category from real feedback text.

    Returns:
        {
            "issue": str,
            "confidence": float,
            "evidence": str
        }
    """

    text = str(text or "").strip().lower()

    if not text:
        return {
            "issue": "Other",
            "confidence": 0.0,
            "evidence": "",
        }

    best_issue = "Other"
    best_matches = []

    for category, words in CATEGORY_KEYWORDS.items():

        matches = [
            word
            for word in words
            if word in text
        ]

        if len(matches) > len(best_matches):
            best_issue = category
            best_matches = matches

    confidence = min(
        1.0,
        len(best_matches) / 2.0,
    )

    return {
        "issue": best_issue,
        "confidence": confidence,
        "evidence": ", ".join(best_matches),
    }


# ============================================================
# FEEDBACK CLASSIFICATION
# ============================================================

def classify_feedback(text: str):

    text = str(text or "").lower()

    category = "General"

    for name, words in CATEGORY_KEYWORDS.items():

        if any(
            word in text
            for word in words
        ):
            category = name
            break

    severity = "medium"

    if any(
        word in text
        for word in CRITICAL_WORDS
    ):
        severity = "critical"

    elif any(
        word in text
        for word in HIGH_WORDS
    ):
        severity = "high"

    return category, severity


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority_score(severity: str) -> float:

    return {
        "critical": 100.0,
        "high": 75.0,
        "medium": 50.0,
        "low": 25.0,
    }.get(
        str(severity or "medium").lower(),
        50.0,
    )


# ============================================================
# UNIQUE ISSUE KEY
# ============================================================

def generate_issue_key(db) -> str:

    while True:

        key = (
            f"ISS-"
            f"{uuid4().hex[:10].upper()}"
        )

        existing = db.scalar(
            select(Issue.id).where(
                Issue.issue_key == key
            )
        )

        if existing is None:
            return key


# ============================================================
# GENERATE ISSUES
# ============================================================

def generate_issues():

    with SessionLocal() as db:

        feedback_records = db.scalars(
            select(Feedback).where(
                Feedback.status == "new"
            )
        ).all()

        if not feedback_records:
            return 0

        grouped = defaultdict(list)

        for feedback in feedback_records:

            category, severity = (
                classify_feedback(
                    feedback.feedback_text
                )
            )

            grouped[
                (category, severity)
            ].append(feedback)

        created = 0

        for (
            category,
            severity,
        ), records in grouped.items():

            issue_key = generate_issue_key(
                db
            )

            priority_score = (
                calculate_priority_score(
                    severity
                )
            )

            issue = Issue(
                issue_key=issue_key,
                title=(
                    f"{category} "
                    f"Customer Issue"
                ),
                description=(
                    "Automatically detected from "
                    f"{len(records)} real feedback "
                    "records."
                ),
                category=category,
                severity=severity,
                priority_score=priority_score,
                occurrence_count=len(records),
                status="open",
            )

            db.add(issue)
            db.flush()

            for feedback in records:

                db.add(
                    IssueFeedback(
                        issue_id=issue.id,
                        feedback_id=feedback.id,
                    )
                )

                feedback.status = "linked"

            created += 1

        db.commit()

        return created