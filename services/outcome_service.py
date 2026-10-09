from datetime import datetime
from sqlalchemy import select, func
from db.engine import SessionLocal
from db.models import IssueIntervention, InterventionOutcome


def create_outcome_measurement(intervention_id, before_count, after_count, remarks=None):
    with SessionLocal() as db:
        intervention = db.get(IssueIntervention, intervention_id)
        if intervention is None:
            raise ValueError("Intervention not found.")
        before_count = int(before_count)
        after_count = int(after_count)
        improvement = ((before_count - after_count) / before_count * 100) if before_count > 0 else 0.0
        outcome = InterventionOutcome(
            intervention_id=intervention_id,
            before_count=before_count,
            after_count=after_count,
            improvement_percentage=round(improvement, 2),
            remarks=remarks,
            measured_at=datetime.utcnow(),
        )
        db.add(outcome)
        db.commit()
        db.refresh(outcome)
        return outcome.id


def get_intervention_outcomes(intervention_id):
    with SessionLocal() as db:
        return db.scalars(
            select(InterventionOutcome)
            .where(InterventionOutcome.intervention_id == intervention_id)
            .order_by(InterventionOutcome.measured_at.desc())
        ).all()


def get_effectiveness_summary():
    with SessionLocal() as db:
        total = db.scalar(select(func.count(InterventionOutcome.id))) or 0
        improving = db.scalar(select(func.count(InterventionOutcome.id)).where(InterventionOutcome.improvement_percentage > 0)) or 0
        worsening = db.scalar(select(func.count(InterventionOutcome.id)).where(InterventionOutcome.improvement_percentage < 0)) or 0
        unchanged = total - improving - worsening
        return {"total": total, "improving": improving, "worsening": worsening, "unchanged": unchanged}
