from sqlalchemy import select, func

from db.engine import SessionLocal
from db.models import (
    Issue,
    IssueFeedback,
)


def generate_recommendations(issue_id):

    with SessionLocal() as db:

        issue = db.get(Issue, issue_id)

        feedback_count = db.scalar(
            select(
                func.count(IssueFeedback.id)
            ).where(
                IssueFeedback.issue_id == issue_id
            )
        )

        recommendations = []

        if issue.severity == "critical":

            recommendations.append(
                {
                    "priority": "Critical",
                    "action": "Escalate immediately to executive leadership.",
                    "reason": "Critical operational risk detected.",
                }
            )

        if feedback_count >= 20:

            recommendations.append(
                {
                    "priority": "High",
                    "action": "Perform detailed root cause investigation.",
                    "reason": "Large volume of similar customer complaints.",
                }
            )

        if issue.category == "Payment":

            recommendations.append(
                {
                    "priority": "High",
                    "action": "Audit payment gateway and transaction logs.",
                    "reason": "Payment failures are increasing.",
                }
            )

        if issue.category == "Delivery":

            recommendations.append(
                {
                    "priority": "Medium",
                    "action": "Review logistics SLA and warehouse dispatch.",
                    "reason": "Delivery delays detected.",
                }
            )

        if not recommendations:

            recommendations.append(
                {
                    "priority": "Medium",
                    "action": "Continue monitoring recurrence.",
                    "reason": "Operational evidence is limited.",
                }
            )

        return recommendations