from sqlalchemy import select, func

from db.engine import SessionLocal

from db.models import (
    Issue,
    IssueFeedback,
    Feedback,
)


def generate_recommendations(
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

        feedback_count = db.scalar(
            select(
                func.count(
                    IssueFeedback.id
                )
            )
            .where(
                IssueFeedback.issue_id
                == issue_id
            )
        ) or 0

        recommendations = []

        # ---------------------------------------------
        # CRITICAL
        # ---------------------------------------------

        if issue.severity == "critical":

            recommendations.append(
                {
                    "priority": "critical",
                    "action":
                        "Escalate the issue "
                        "to the responsible "
                        "department immediately.",
                    "reason":
                        "Issue severity is critical.",
                }
            )

        # ---------------------------------------------
        # HIGH OCCURRENCE
        # ---------------------------------------------

        if (
            issue.occurrence_count
            and issue.occurrence_count >= 10
        ):

            recommendations.append(
                {
                    "priority": "high",
                    "action":
                        "Perform root-cause "
                        "investigation.",
                    "reason":
                        "Repeated feedback indicates "
                        "a systemic problem.",
                }
            )

        # ---------------------------------------------
        # MANY LINKED FEEDBACK RECORDS
        # ---------------------------------------------

        if feedback_count >= 20:

            recommendations.append(
                {
                    "priority": "high",
                    "action":
                        "Review all linked feedback "
                        "for common contributing "
                        "factors.",
                    "reason":
                        "Large number of customer "
                        "records are associated "
                        "with this issue.",
                }
            )

        # ---------------------------------------------
        # SLA
        # ---------------------------------------------

        if issue.status not in [
            "resolved",
            "verified",
            "closed",
        ]:

            recommendations.append(
                {
                    "priority": "medium",
                    "action":
                        "Review SLA status and "
                        "assign an accountable "
                        "owner.",
                    "reason":
                        "Issue remains operationally "
                        "active.",
                }
            )

        # ---------------------------------------------
        # DEFAULT
        # ---------------------------------------------

        if not recommendations:

            recommendations.append(
                {
                    "priority": "medium",
                    "action":
                        "Continue investigation "
                        "and monitor recurrence.",
                    "reason":
                        "Insufficient operational "
                        "evidence for a stronger "
                        "recommendation.",
                }
            )

        return recommendations