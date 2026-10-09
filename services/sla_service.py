from datetime import datetime
from sqlalchemy import select

from db.engine import SessionLocal
from db.models import IssueIntervention


def get_sla_records():

    with SessionLocal() as db:

        interventions = db.scalars(
            select(IssueIntervention)
        ).all()

        results = []

        today = datetime.utcnow()

        for item in interventions:

            if item.status == "completed":

                sla = "Completed"

            elif item.due_date is None:

                sla = "No Due Date"

            elif today > item.due_date:

                sla = "Breached"

            else:

                sla = "Within SLA"

            results.append(
                {
                    "id": item.id,
                    "owner": item.owner,
                    "department": item.assigned_department,
                    "priority": item.priority,
                    "status": item.status,
                    "due_date": item.due_date,
                    "sla": sla,
                }
            )

        return results