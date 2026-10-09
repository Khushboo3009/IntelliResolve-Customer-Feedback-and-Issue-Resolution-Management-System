from sqlalchemy import (
    select,
    func,
)

from db.engine import SessionLocal

from db.models import (
    Issue,
)


# ============================================================
# RECURRENCE SCORE
# ============================================================

def calculate_recurrence_score(
    issue,
):

    with SessionLocal() as db:

        title = str(
            getattr(
                issue,
                "title",
                "",
            )
            or ""
        ).lower()

        if not title:

            return {
                "recurrence_score": 0,
                "recurring": False,
                "similar_count": 0,
            }

        words = [
            word.strip()
            for word in title.split()
            if len(word.strip()) >= 4
        ]

        if not words:

            return {
                "recurrence_score": 0,
                "recurring": False,
                "similar_count": 0,
            }

        # Search using first significant word.
        keyword = words[0]

        issues = db.scalars(
            select(Issue)
            .where(
                Issue.title.ilike(
                    f"%{keyword}%"
                )
            )
            .limit(100)
        ).all()

        similar_count = max(
            0,
            len(issues) - 1,
        )

        if similar_count >= 10:

            score = 100

        elif similar_count >= 5:

            score = 80

        elif similar_count >= 3:

            score = 60

        elif similar_count >= 1:

            score = 35

        else:

            score = 0

        return {
            "recurrence_score":
                score,

            "recurring":
                similar_count > 0,

            "similar_count":
                similar_count,
        }