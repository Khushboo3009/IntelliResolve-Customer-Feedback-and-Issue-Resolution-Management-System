from services.sla_service import get_sla_records


def generate_alerts():

    alerts = []

    for record in get_sla_records():

        if record["sla"] == "Breached":

            alerts.append(
                {
                    "level": "Critical",
                    "title": "SLA Breach",
                    "message":
                        f"{record['department']} intervention "
                        f"owned by {record['owner']} is overdue.",
                }
            )

        elif record["priority"] == "Critical":

            alerts.append(
                {
                    "level": "High",
                    "title": "Critical Intervention",
                    "message":
                        f"{record['department']} requires immediate action.",
                }
            )

    return alerts