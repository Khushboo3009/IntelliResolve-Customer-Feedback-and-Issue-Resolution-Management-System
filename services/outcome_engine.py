from datetime import datetime
from sqlalchemy import select, func
from db.engine import SessionLocal
from db.models import IssueIntervention, InterventionOutcome, IssueFeedback, Feedback


def calculate_outcome(intervention_id):
    """Calculate a real before/after complaint count for one intervention."""
    with SessionLocal() as db:
        intervention = db.get(IssueIntervention, intervention_id)
        if intervention is None:
            raise ValueError("Intervention not found.")
        if intervention.started_at is None:
            raise ValueError("Intervention has not started.")

        feedback_ids = select(IssueFeedback.feedback_id).where(
            IssueFeedback.issue_id == intervention.issue_id
        )
        before_count = db.scalar(
            select(func.count(Feedback.id)).where(
                Feedback.id.in_(feedback_ids),
                Feedback.created_at < intervention.started_at,
            )
        ) or 0
        after_count = db.scalar(
            select(func.count(Feedback.id)).where(
                Feedback.id.in_(feedback_ids),
                Feedback.created_at >= intervention.started_at,
            )
        ) or 0
        improvement = 0.0
        if before_count > 0:
            improvement = ((before_count - after_count) / before_count) * 100
        improvement = round(max(-100.0, min(100.0, improvement)), 2)

        outcome = db.scalar(
            select(InterventionOutcome).where(
                InterventionOutcome.intervention_id == intervention_id
            )
        )
        if outcome is None:
            outcome = InterventionOutcome(intervention_id=intervention_id)
            db.add(outcome)
        outcome.before_count = before_count
        outcome.after_count = after_count
        outcome.improvement_percentage = improvement
        outcome.remarks = "Calculated from feedback linked to the intervention's issue."
        outcome.measured_at = datetime.utcnow()
        db.commit()
        db.refresh(outcome)
        return outcome
