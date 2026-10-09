from datetime import datetime
from sqlalchemy import select

from db.engine import SessionLocal
from db.models import Issue

from services.risk_engine import calculate_issue_risk
from services.trend_engine import calculate_issue_trend
from services.recurrence_engine import calculate_recurrence_score
from services.recommendation_engine import generate_recommendations


# ============================================================
# BUSINESS IMPACT CALCULATOR
# ============================================================

def calculate_business_impact(issue):
    occurrences = getattr(issue, "occurrence_count", 0) or 0

    severity = str(
        getattr(issue, "severity", "medium")
    ).lower().strip()

    multiplier = {
        "critical": 1.00,
        "high": 0.75,
        "medium": 0.50,
        "low": 0.25,
    }.get(severity, 0.40)

    impact_value = occurrences * multiplier

    if impact_value >= 1000:
        score = 100
    elif impact_value >= 500:
        score = 85
    elif impact_value >= 250:
        score = 70
    elif impact_value >= 100:
        score = 55
    elif impact_value >= 50:
        score = 40
    else:
        score = 20

    return {
        "impact_value": round(impact_value, 2),
        "impact_score": score,
    }


# ============================================================
# PREDICT SINGLE ISSUE
# ============================================================

def predict_issue(issue_id):

    with SessionLocal() as db:

        issue = db.get(Issue, issue_id)

        if issue is None:
            raise ValueError(f"Issue {issue_id} not found.")

        # Trend Analysis
        trend = calculate_issue_trend(issue_id)

        # Recurrence Analysis
        recurrence = calculate_recurrence_score(issue)

        # Business Impact
        business = calculate_business_impact(issue)

        # Risk Score
        risk = calculate_issue_risk(
            issue=issue,
            growth_score=trend.get("growth_score", 0),
            recurrence_score=recurrence.get("recurrence_score", 0),
            business_impact_score=business.get("impact_score", 0),
        )

        # AI Recommendations
        recommendations = generate_recommendations(issue_id)

        # Final Output
        return {
            # Identity
            "issue_id": issue.id,
            "issue_key": getattr(issue, "issue_key", f"ISS-{issue.id}"),
            "title": getattr(issue, "title", "Untitled Issue"),
            "severity": getattr(issue, "severity", "Medium"),
            "category": getattr(issue, "category", "General"),

            # Risk
            "risk_score": risk.get("risk_score", 0),
            "risk_level": risk.get("risk_level", "low"),

            # Component Scores
            "severity_score": risk.get("severity_score", 0),
            "occurrence_score": risk.get("occurrence_score", 0),
            "growth_score": risk.get("growth_score", 0),
            "sla_score": risk.get("sla_score", 0),
            "recurrence_score": risk.get("recurrence_score", 0),
            "business_impact_score": risk.get(
                "business_impact_score", 0
            ),

            # Trend
            "growth_percentage": trend.get(
                "growth_percentage", 0
            ),
            "trend_direction": trend.get(
                "trend_direction", "Stable"
            ),

            # Recurrence
            "recurring": recurrence.get("recurring", False),
            "similar_count": recurrence.get("similar_count", 0),

            # Business
            "business_impact": business.get("impact_value", 0),

            # Recommendations
            "recommendations": recommendations,

            # Timestamp
            "calculated_at": datetime.utcnow(),
        }


# ============================================================
# PREDICT ALL ACTIVE ISSUES
# ============================================================

def predict_active_issues():

    with SessionLocal() as db:

        issues = db.scalars(
            select(Issue).where(
                Issue.status.notin_(["resolved", "closed"])
            )
        ).all()

    results = []

    for issue in issues:

        try:

            prediction = predict_issue(issue.id)
            results.append(prediction)

        except Exception as exc:

            results.append({
                "issue_id": issue.id,
                "issue_key": f"ISS-{issue.id}",
                "title": "Prediction Failed",
                "severity": "Unknown",
                "category": "General",

                "risk_score": 0,
                "risk_level": "error",

                "severity_score": 0,
                "occurrence_score": 0,
                "growth_score": 0,
                "sla_score": 0,
                "recurrence_score": 0,
                "business_impact_score": 0,

                "growth_percentage": 0,
                "trend_direction": "Unknown",

                "recurring": False,
                "similar_count": 0,
                "business_impact": 0,

                "recommendations": [],

                "error": str(exc),
                "calculated_at": datetime.utcnow(),
            })

    results.sort(
        key=lambda x: x.get("risk_score", 0),
        reverse=True,
    )

    return results