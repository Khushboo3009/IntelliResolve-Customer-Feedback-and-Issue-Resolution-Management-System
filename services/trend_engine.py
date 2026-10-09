from datetime import datetime, timedelta

from sqlalchemy import (
    select,
    func,
)

from db.engine import SessionLocal

from db.models import (
    Issue,
    Feedback,
)


# ============================================================
# TREND ANALYSIS
# ============================================================

def calculate_issue_trend(
    issue_id,
):

    with SessionLocal() as db:

        issue = db.get(
            Issue,
            issue_id,
        )

        if issue is None:

            return {
                "growth_percentage": 0,
                "trend_direction": "unknown",
                "growth_score": 0,
            }

        issue_created = getattr(
            issue,
            "created_at",
            None,
        )

        if not issue_created:

            return {
                "growth_percentage": 0,
                "trend_direction": "unknown",
                "growth_score": 0,
            }

        now = datetime.utcnow()

        recent_start = (
            now - timedelta(days=7)
        )

        previous_start = (
            now - timedelta(days=14)
        )

        # ----------------------------------------------------
        # Current period
        # ----------------------------------------------------

        recent_count = db.scalar(
            select(
                func.count(
                    Feedback.id
                )
            )
            .where(
                Feedback.created_at
                >= recent_start
            )
        ) or 0

        # ----------------------------------------------------
        # Previous period
        # ----------------------------------------------------

        previous_count = db.scalar(
            select(
                func.count(
                    Feedback.id
                )
            )
            .where(
                Feedback.created_at
                >= previous_start
            )
            .where(
                Feedback.created_at
                < recent_start
            )
        ) or 0

        if previous_count == 0:

            if recent_count > 0:

                growth = 100

            else:

                growth = 0

        else:

            growth = (
                (
                    recent_count
                    - previous_count
                )
                / previous_count
            ) * 100

        growth = round(
            growth,
            2,
        )

        if growth >= 30:

            direction = "rapidly_increasing"
            score = 100

        elif growth >= 15:

            direction = "increasing"
            score = 75

        elif growth >= 5:

            direction = "slightly_increasing"
            score = 50

        elif growth <= -15:

            direction = "decreasing"
            score = 15

        else:

            direction = "stable"
            score = 25

        return {
            "growth_percentage":
                growth,

            "trend_direction":
                direction,

            "growth_score":
                score,

            "recent_count":
                recent_count,

            "previous_count":
                previous_count,
        }