from datetime import datetime

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Issue,
    Feedback,
)


# ============================================================
# SAFE NORMALIZATION
# ============================================================

def clamp(value, minimum=0, maximum=100):

    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


# ============================================================
# SEVERITY SCORE
# ============================================================

def severity_score(severity):

    severity = (
        str(severity or "")
        .lower()
        .strip()
    )

    mapping = {

        "critical": 100,
        "high": 80,
        "medium": 55,
        "low": 25,

    }

    return mapping.get(
        severity,
        40,
    )


# ============================================================
# OCCURRENCE SCORE
# ============================================================

def occurrence_score(
    occurrence_count,
):

    try:

        value = float(
            occurrence_count or 0
        )

    except Exception:

        value = 0

    if value >= 1000:
        return 100

    if value >= 500:
        return 90

    if value >= 250:
        return 80

    if value >= 100:
        return 65

    if value >= 50:
        return 50

    if value >= 10:
        return 35

    return 15


# ============================================================
# SLA SCORE
# ============================================================

def calculate_sla_score(issue):

    deadline = getattr(
        issue,
        "sla_deadline",
        None,
    )

    if not deadline:

        return 0

    status = str(
        getattr(
            issue,
            "status",
            "",
        ) or ""
    ).lower()

    if status in (
        "resolved",
        "closed",
    ):

        return 0

    now = datetime.utcnow()

    if deadline < now:

        return 100

    remaining = (
        deadline - now
    ).total_seconds()

    hours = (
        remaining / 3600
    )

    if hours <= 6:
        return 90

    if hours <= 24:
        return 70

    if hours <= 48:
        return 45

    return 10


# ============================================================
# RISK LEVEL
# ============================================================

def risk_level(score):

    if score >= 80:
        return "critical"

    if score >= 60:
        return "high"

    if score >= 35:
        return "medium"

    return "low"


# ============================================================
# ISSUE RISK
# ============================================================

def calculate_issue_risk(
    issue,
    growth_score=0,
    recurrence_score=0,
    business_impact_score=0,
):

    severity = severity_score(
        getattr(
            issue,
            "severity",
            None,
        )
    )

    occurrences = occurrence_score(
        getattr(
            issue,
            "occurrence_count",
            0,
        )
    )

    sla = calculate_sla_score(
        issue
    )

    growth_score = clamp(
        growth_score
    )

    recurrence_score = clamp(
        recurrence_score
    )

    business_impact_score = clamp(
        business_impact_score
    )

    score = (

        severity * 0.25

        + occurrences * 0.20

        + growth_score * 0.20

        + sla * 0.15

        + recurrence_score * 0.10

        + business_impact_score * 0.10
    )

    score = round(
        clamp(score),
        2,
    )

    return {
        "risk_score": score,

        "risk_level":
            risk_level(score),

        "severity_score":
            severity,

        "occurrence_score":
            occurrences,

        "growth_score":
            growth_score,

        "sla_score":
            sla,

        "recurrence_score":
            recurrence_score,

        "business_impact_score":
            business_impact_score,
    }