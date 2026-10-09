import json
from datetime import datetime

from sqlalchemy import select

from db.engine import SessionLocal

from db.models import (
    Feedback,
    FeedbackAnalysis,
)

from services.feedback_analyzer import (
    analyze_feedback,
)


# ============================================================
# KEYWORD SERIALIZATION
# ============================================================

def serialize_keywords(keywords):
    """
    Convert extracted keywords into a database-safe string.

    The FeedbackAnalysis.keywords column is a MySQL TEXT column,
    so Python lists must be serialized before being stored.
    """

    if keywords is None:
        return ""

    # Already a string.
    if isinstance(keywords, str):
        return keywords.strip()

    # Lists, tuples, sets, etc.
    if isinstance(keywords, (list, tuple, set)):
        return json.dumps(
            list(keywords),
            ensure_ascii=False,
        )

    # Any unexpected value.
    return json.dumps(
        [str(keywords)],
        ensure_ascii=False,
    )


# ============================================================
# KEYWORD DESERIALIZATION
# ============================================================

def deserialize_keywords(value):
    """
    Convert the database TEXT representation back into a
    Python list.

    This helper is useful for UI/services that need to display
    individual keywords.
    """

    if not value:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    try:
        parsed = json.loads(
            str(value)
        )

        if isinstance(parsed, list):
            return parsed

    except (
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ):
        pass

    # Backward compatibility for old comma-separated values.
    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


# ============================================================
# ANALYZE PENDING FEEDBACK
# ============================================================

def analyze_pending_feedback(
    batch_size=500,
):
    """
    Analyze real feedback records stored in MySQL.

    Only feedback records that have not already been analyzed
    are processed.

    Each feedback record is handled independently so that one
    problematic record does not prevent the remaining records
    from being analyzed.
    """

    try:
        batch_size = int(batch_size)
    except (
        TypeError,
        ValueError,
    ):
        batch_size = 500

    batch_size = max(
        1,
        batch_size,
    )

    with SessionLocal() as db:

        feedback_records = db.scalars(
            select(Feedback)
            .where(
                Feedback.processing_status == "pending"
            )
            .where(
                Feedback.feedback_text.is_not(None)
            )
            .limit(batch_size)
        ).all()

        if not feedback_records:
            return {
                "processed": 0,
                "failed": 0,
            }

        processed = 0
        failed = 0

        for feedback in feedback_records:

            try:
                # ------------------------------------------------
                # Run the actual feedback analysis.
                # ------------------------------------------------

                result = analyze_feedback(
                    feedback.feedback_text,
                    feedback.category,
                )

                if not isinstance(
                    result,
                    dict,
                ):
                    raise ValueError(
                        "Feedback analyzer returned "
                        "an invalid result."
                    )

                # ------------------------------------------------
                # Find existing analysis record.
                # ------------------------------------------------

                analysis = db.scalar(
                    select(FeedbackAnalysis)
                    .where(
                        FeedbackAnalysis.feedback_id
                        == feedback.id
                    )
                )

                # ------------------------------------------------
                # Create analysis record if necessary.
                # ------------------------------------------------

                if analysis is None:

                    analysis = FeedbackAnalysis(
                        feedback_id=feedback.id
                    )

                    db.add(analysis)

                # ------------------------------------------------
                # Basic analysis fields.
                # ------------------------------------------------

                analysis.sentiment = (
                    result.get(
                        "sentiment",
                        "Neutral",
                    )
                )

                analysis.sentiment_score = (
                    result.get(
                        "sentiment_score",
                        0.0,
                    )
                )

                analysis.detected_category = (
                    result.get(
                        "detected_category",
                        "General",
                    )
                )

                analysis.category_confidence = (
                    result.get(
                        "category_confidence",
                        0.0,
                    )
                )

                analysis.priority = (
                    result.get(
                        "priority",
                        "Low",
                    )
                )

                analysis.priority_score = (
                    result.get(
                        "priority_score",
                        0.0,
                    )
                )

                analysis.is_complaint = bool(
                    result.get(
                        "is_complaint",
                        False,
                    )
                )

                # ------------------------------------------------
                # IMPORTANT:
                #
                # keywords may be returned as:
                #
                # [
                #     "redmi",
                #     "battery",
                #     "phone"
                # ]
                #
                # But the DB column is TEXT.
                #
                # Therefore serialize the list to JSON.
                # ------------------------------------------------

                analysis.keywords = serialize_keywords(
                    result.get(
                        "keywords",
                        "",
                    )
                )

                # ------------------------------------------------
                # Issue-related analysis.
                # ------------------------------------------------

                analysis.evidence = result.get(
                    "evidence"
                )

                analysis.issue_type = result.get(
                    "issue_type"
                )

                analysis.issue_confidence = (
                    result.get(
                        "issue_confidence",
                        0.0,
                    )
                )

                # ------------------------------------------------
                # Timestamps.
                # ------------------------------------------------

                now = datetime.utcnow()

                analysis.analyzed_at = now
                analysis.processed_at = now

                # ------------------------------------------------
                # Update feedback.
                # ------------------------------------------------

                feedback.sentiment = result.get(
                    "sentiment",
                    "Neutral",
                )

                feedback.processing_status = (
                    "analyzed"
                )

                feedback.processed_at = now

                # ------------------------------------------------
                # Flush this record.
                #
                # This catches database problems here rather than
                # waiting until the final batch commit.
                # ------------------------------------------------

                db.flush()

                processed += 1

            except Exception as exc:

                # ------------------------------------------------
                # Roll back the failed record.
                # ------------------------------------------------

                db.rollback()

                failed += 1

                print(
                    f"Feedback {feedback.id} "
                    f"analysis failed: {exc}"
                )

                # ------------------------------------------------
                # Re-fetch the feedback object after rollback.
                # ------------------------------------------------

                failed_feedback = db.get(
                    Feedback,
                    feedback.id,
                )

                if failed_feedback is not None:
                    failed_feedback.processing_status = (
                        "analysis_failed"
                    )

                    try:
                        db.commit()
                    except Exception:
                        db.rollback()

        # --------------------------------------------------------
        # Final commit.
        # --------------------------------------------------------

        try:
            db.commit()

        except Exception as exc:

            db.rollback()

            print(
                f"Feedback analysis batch commit failed: {exc}"
            )

            return {
                "processed": 0,
                "failed": len(feedback_records),
            }

        return {
            "processed": processed,
            "failed": failed,
        }